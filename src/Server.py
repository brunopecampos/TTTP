import select
import json
import time
from Database import Database
from NetworkHandler import NetworkHandler, TCP, UDP, BUFFER_SIZE
from ServerAutomata import TransitionMachine, InitialState, CommandList

class Server():
    def __init__(self, port):
        self.port = port
        self.tcp_socket = None
        self.udp_socket = None
        self.db = Database('./db.json')
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
        get client identifier from client socket
        """
        addr = client_socket.getpeername()
        return f"{addr[0]}:{addr[1]}"

    def handle_tcp_socket(self, s):
        """
        handle a new incoming tcp connection
        """
        client_socket, address = s.accept()

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

        if not data:
            self.remove_client(s)
            s.close()
            return

        argv = data.decode('utf-8').split()
        args = argv[1:]

        # validate cmd
        cmd = argv[0]
        reply = ''
        if cmd not in CommandList:
            reply = 'CERR'
            s.send(reply.encode())
            return

        # validate cmd formatting
        expected_args = CommandList[cmd]['args']
        if len(args) != expected_args:
            reply = f'{cmd} 400'
            s.send(reply.encode())
            return

        # validate state transition
        client_id = self.get_client_id(s)
        client = self.clients[client_id]
        current_state = client['state']
        next_state = CommandList[cmd]['state']

        if next_state != ''
            possible_incoming_states = TransitionMachine[next_state]
            if current_state not in possible_incoming_states:
                reply = f'{cmd} 403'
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
        ack = b'HELO 200'
        socket.send(ack)
        return True

    def exec_cmd_ping(self, socket, args):
        ack = b'PING 200'
        socket.send(ack)
        return True

    def exec_cmd_pinl(self, socket, args):
        ack = 'PINL 200\n'
        now = str(int(time.clock_gettime(0)))
        reply = ack + now
        socket.send(reply.encode())
        return True
    
    def exec_cmd_nusr(self, socket, args):
        db = self.db
        success = False
        username = args[0]
        password = args[1]
        if db.user_exists(username):
            reply = b'NUSR 403'
        else:
            db.add_user(username, password)
            reply = b'NUSR 201'
            success = True
        socket.send(reply)
        return success

    def exec_cmd_logn(self, socket, args):
        db = self.db
        success = False
        username = args[0]
        passwd = args[1]
        if db.user_exists(username):
            reply = 'LOGN 403\nErro: usuário não existe'
        elif username in self.username2ip:
            reply = 'LOGN 403\nErro: usuário já conectado'
        elif not db.can_user_log_in(username, passwd):
            reply = 'LOGN 403\nErro: senha incorreta'
        else:
            id = self.get_client_id(socket)
            self.clients[id]['username'] = username
            self.username2ip[username] = id
            reply = 'LOGN 200'
            success = True
        socket.send(reply.encode('utf-8'))
        return success

    def exec_cmd_lout(self, socket, args):
        success = False
        reply = 'LOUT 403'

        id = self.get_client_id(socket)
        username = self.clients[id]['username']

        for user in self.username2ip:
            if user == username:
                self.username2ip.pop(username)
                reply = 'LOUT 200'
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
            reply = 'GTIP 401'
            success = False
        else:
            addr = self. username2ip[user]
            ip = addr.split(":")[0]
            reply = f'GTIP 200\n{ip}'
            success = True
        socket.send(reply.encode())
        return success

    def exec_cmd_mstr(self, socket, args):
        db = self.db
        user1 = args[0]
        user2 = args[1]
        users = self.username2ip

        if not (user1 in users and user2 in users):
            reply = 'MSTR 401'
            success = False
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
            reply = f'MSTR 200\n{matchid}'
            success= True

        socket.send(reply.encode())
        return success

    def exec_cmd_mend(self, socket, args):
        matchid = args[0]
        winner = args[1]
        pass

    def exec_cmd_gbye(self, socket, args):
        self.remove_client(socket)
        socket.send(b'GBYE 200')
        socket.close()
        return True
