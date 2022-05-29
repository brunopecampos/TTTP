import select
import time
from Database import Database
from NetworkHandler import NetworkHandler, TCP, UDP, BUFFER_SIZE
from ServerAutomata import TransitionMachine, InitialState, CommandList

class Server():
    def __init__(self, port):
        self.port = port
        self.tcp_socket = None
        self.udp_socket = None
        self.db = Database('db.json')
        self.sockets = [] # all sockets (server + client sockets)
        self.clients = {} # information about the client (username, state)
        self.username2ip = {} # iplookup

    def start(self):
        """
        start and run server
        """
        nw_tcp = NetworkHandler(TCP)
        nw_udp = NetworkHandler(UDP)
        nw_tcp.listen(self.port) # start tcp listener
        self.tcp_socket = nw_tcp.get_socket()
        self.udp_socket = nw_udp.get_socket()
        self.sockets = [self.tcp_socket]
        self.run()

    def run(self):
        """
        run server forever
        """
        while True:
            readable, writable, errorable = select.select(self.sockets, [], [])
            for s in readable:
                if s is self.tcp_socket:
                    self.handle_tcp_socket(s)
                else:
                    self.handle_client_socket(s)

    def get_client_id(self, client_socket):
        """
        get client identifier for given client socket
        """
        addr = client_socket.getpeername()
        return f"{addr[0]}:{addr[1]}"

    def get_client_username(self, client_socket):
        """
        get client username for given client socket
        """
        cid = self.get_client_id(client_socket)
        return self.clients[cid]['username']

    def handle_tcp_socket(self, s):
        """
        handle a new incoming tcp connection
        """
        client_socket, address = s.accept()

        print(f"got new connection from {address}")

        # add client socket
        self.sockets.append(client_socket)

        # add client state
        client_id = f"{address[0]}:{address[1]}"
        client = {
            'username': '',
            'state': InitialState,
        }
        self.clients[client_id] = client

    def remove_client(self, client_socket):
        """
        remove client, but do not close socket
        """

        # get client id, which is its INET address
        client_id = self.get_client_id(client_socket)

        # get its username, if any
        username = self.clients[client_id]['username']

        # if it is logged in, delete it from array of active users
        if username in self.username2ip:
            self.username2ip.pop(username)

        # remove socket from sockets array
        self.sockets.remove(client_socket)

        # remove client from client info array
        self.clients.pop(client_id)

    def handle_client_socket(self, s):
        """
        handle already existing connection to client
        """
        data = s.recv(BUFFER_SIZE)

        # no data was read
        if not data:
            self.remove_client(s)
            s.close()
            return

        # try read data and decode it
        try:
            argv = data.decode().split()
        except UnicodeDecodeError:
            reply = 'CERR\n'
            self.remove_client(s)
            s.send(reply.encode())
            s.close()
            return

        args = argv[1:]

        # validate cmd
        if len(argv) == 0 or argv[0] not in CommandList:
            reply = 'CERR\n'
            s.send(reply.encode())
            return

        cmd = argv[0]

        # validate cmd formatting
        expected_args = CommandList[cmd]['args']
        if len(args) != expected_args:
            reply = f'{cmd} 400\n'
            s.send(reply.encode())
            return

        # validate state transition
        client_id = self.get_client_id(s)
        client = self.clients[client_id]
        current_state = client['state']
        next_state = CommandList[cmd]['next_state']

        if current_state == InitialState and cmd != 'HELO':
            reply = f'{cmd} 400\n'
            s.send(reply.encode())
            return

        if next_state != '':
            possible_incoming_states = TransitionMachine[next_state]
            if current_state not in possible_incoming_states:
                reply = f'{cmd} 403\n'
                s.send(reply.encode())
                return

        if self.exec_command(s, cmd, args) and next_state != '':
            client['state'] = next_state

    def exec_command(self, socket, cmd, args):
        """
        execute given command
        """
        # map command to function
        cmd2fn = {
            'HELO': self.exec_cmd_helo,
            'PING': self.exec_cmd_ping,
            'PINL': self.exec_cmd_pinl,
            'NUSR': self.exec_cmd_nusr,
            'LOGN': self.exec_cmd_logn,
            'LOUT': self.exec_cmd_lout,
            'USRL': self.exec_cmd_usrl,
            'UHOF': self.exec_cmd_uhof,
            'GTIP': self.exec_cmd_gtip,
            'MSTR': self.exec_cmd_mstr,
            'MEND': self.exec_cmd_mend,
            'GBYE': self.exec_cmd_gbye,
        }
        return cmd2fn[cmd](socket, args)

    def exec_cmd_helo(self, socket, args):
        ack = b'HELO 200\n'
        socket.send(ack)
        return True

    def exec_cmd_ping(self, socket, args):
        ack = b'PING 200\n'
        socket.send(ack)
        return True

    def exec_cmd_pinl(self, socket, args):
        ack = 'PINL 200\n'
        now = str(int(time.clock_gettime(0)))
        reply = ack + now + '\n'
        socket.send(reply.encode())
        return True
    
    def exec_cmd_nusr(self, socket, args):
        db = self.db
        success = False
        username = args[0]
        password = args[1]
        if db.user_exists(username):
            reply = 'NUSR 403\nErro: usuário já existe'
        else:
            db.add_user(username, password)
            reply = 'NUSR 201\n'
            success = True
        socket.send(reply.encode())
        return success

    def exec_cmd_logn(self, socket, args):
        db = self.db
        success = False
        username = args[0]
        passwd = args[1]
        if not db.user_exists(username):
            reply = 'LOGN 403\nErro: usuário não existe\n'
        elif username in self.username2ip:
            reply = 'LOGN 403\nErro: usuário já conectado\n'
        elif not db.can_user_log_in(username, passwd):
            reply = 'LOGN 403\nErro: senha incorreta\n'
        else:
            id = self.get_client_id(socket)
            self.clients[id]['username'] = username
            self.username2ip[username] = id
            reply = 'LOGN 200\n'
            success = True
        socket.send(reply.encode('utf-8'))
        return success

    def exec_cmd_lout(self, socket, args):
        success = False
        reply = 'LOUT 403\nErro: usuário não está logado'

        id = self.get_client_id(socket)
        username = self.clients[id]['username']

        for user in self.username2ip:
            if user == username:
                self.username2ip.pop(username)
                reply = 'LOUT 200\n'
                success = True
                break

        socket.send(reply.encode())
        return success

    def exec_cmd_usrl(self, socket, args):
        reply = 'USRL 200\n'
        for user in self.username2ip:
            ip = self.username2ip[user]
            if self.clients[ip]['state'] == 'PLAYING':
                reply += f"{user} *\n"
            else:
                reply += f"{user}\n"
        socket.send(reply.encode()) 
        return True

    def exec_cmd_uhof(self, socket, args):
        reply = 'UHOF 200\n'
        reply += self.db.list_users_by_score()
        socket.send(reply.encode())
        return True

    def exec_cmd_gtip(self, socket, args):
        user = args[0]
        if user not in self.username2ip:
            reply = 'GTIP 404\nErro: Usuário não conectado'
            success = False
        else:
            addr = self. username2ip[user]
            ip = addr.split(":")[0]
            reply = f'GTIP 200\n{ip}'
            success = True
        socket.send(reply.encode())
        return success

    def is_playing(self, username):
        uid = self.username2ip[username]
        return self.clients[uid]['state'] == 'PLAYING'

    def exec_cmd_mstr(self, socket, args):
        db = self.db
        user1 = self.get_client_username(socket)
        user2 = args[0]
        users = self.username2ip
        success = False

        if not (user1 in users and user2 in users):
            reply = 'MSTR 401\nErro: Usuário não está conectado\n'
        elif user1 == user2:
            reply = 'MSTR 400\nErro: Usuário não pode jogar contra si mesmo\n'
        elif self.is_playing(user1) or self.is_playing(user2):
            reply = 'MSTR 403\nErro: Usuário já está jogando\n'
        else:
            # record match in database
            matchid = db.start_match(user1, user2)

            # update state of connected clients
            # this is hardcoded :-(
            uid1 = users[user1]
            uid2 = users[user2]
            self.clients[uid1]['state'] = 'PLAYING'
            self.clients[uid2]['state'] = 'PLAYING'

            # success!
            reply = f'MSTR 200\n{matchid}\n'
            success = True

        socket.send(reply.encode())
        return success

    def exec_cmd_mend(self, socket, args):
        db = self.db
        success = False

        try:
            matchid = int(args[0])
        except ValueError:
            socket.send(b'MEND 400\n')
            return False

        winner = args[1]

        if not db.match_exists(matchid):
            reply = 'MEND 404\nErro: match não existe\n'
        elif not db.record_match(matchid, winner):
            reply = 'MEND 403\nErro: match não pode ser alterado\n'
        else:
            reply = 'MEND 201\n'

            # hardcoded way to change the state of two users
            u1, u2 = db.get_users_from_match(matchid)
            uid1 = self.username2ip[u1]
            uid2 = self.username2ip[u2]
            self.clients[uid1]['state'] = 'LOGGED'
            self.clients[uid2]['state'] = 'LOGGED'
            success = True
        socket.send(reply.encode())
        return success

    def exec_cmd_gbye(self, socket, args):
        self.remove_client(socket)
        socket.send(b'GBYE 200\n')
        socket.close()
        return True
