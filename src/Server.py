import select
import json
import time
from Database import Database
from NetworkHandler import NetworkHandler, TCP, UDP, BUFFER_SIZE

with open('../data/states.json', "r") as f:
    STATES = json.load(f)
with open('../data/commands.json', "r") as f:
    COMMANDS = json.load(f)

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
        nw_tcp = NetworkHandler(TCP)
        nw_udp = NetworkHandler(UDP)
        nw_tcp.listen(self.port) # start tcp listener
        self.tcp_socket = nw_tcp.get_socket()
        self.udp_socket = nw_udp.get_socket()
        self.sockets = [self.tcp_socket]
        self.run()

    def run(self):
        while True:
            readable, writable, errorable = select.select(self.sockets, [], [])
            for s in readable:
                if s is self.tcp_socket:
                    self.handle_tcp_socket(s)
                else:
                    self.handle_client_socket(s)

    def get_client_id(self, client_socket):
        addr = client_socket.getpeername()
        return f"{addr[0]}:{addr[1]}"

    def handle_tcp_socket(self, s):
        client_socket, address = s.accept()

        # add client socket
        self.sockets.append(client_socket)

        # add client state
        client_id = f"{address[0]}:{address[1]}"
        client = {
            'username': '',
            'state': 'NOT_LOGGED',
        }
        self.clients[client_id] = client

    def handle_client_socket(self, s):
        address = s.getpeername()
        client_id = f"{address[0]}:{address[1]}"

        data = s.recv(BUFFER_SIZE)

        if not data:
            s.close()
            self.sockets.remove(s)
            self.clients.pop(client_id)
            return

        argv = data.decode('utf-8').split()
        args = argv[1:]
        client = self.clients[client_id]

        # validate cmd
        cmd = argv[0]
        reply = ''
        if cmd not in COMMANDS:
            reply = 'CERR'
            s.send(reply.encode())
            return

        # validate cmd formatting
        expected_args = COMMANDS[cmd]['args']
        if len(args) != expected_args:
            reply = f'{cmd} 400'
            s.send(reply.encode())
            return

        # validate state transition
        current_state = client['state']
        next_state = COMMANDS[cmd]['state']
        possible_incoming_states = STATES[next_state]

        if current_state not in possible_incoming_states:
            reply = f'{cmd} 403'
            s.send(reply.encode())
            return

        self.exec_command(s, cmd, args)

    def exec_command(self, socket, cmd, args):
        pass

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
        success = False
        user1 = args[0]
        user2 = args[1]
        if not (db.user_exists(user1) and db.user_exists(user2)):
            reply = 'MSTR 401'
        else:
            matchid = db.start_match(user1, user2)
            reply = f'MSTR 200\n{matchid}'
        socket.send(reply.encode())
        return success

    def exec_cmd_mend(self, socket, args):
        matchid = args[0]
        winner = args[1]
        pass

    def exec_cmd_gbye(self, socket, args):
        id = self.get_client_id(socket)
        username = self.clients[id]['username']

        # remove user from active users
        if username in self.username2ip:
            self.username2ip.pop(username)

        # remove client from client state array
        self.clients.pop(id)

        # remove client socket
        self.sockets.remove(socket)

        # close connection
        socket.send(b'GBYE 200')
        socket.close()

        # ok
        return True
