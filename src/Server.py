import threading
import select
import time
from Database import Database
from Logger import Logger
from NetworkHandler import TCP, UDP, BUFFER_SIZE, NetworkHandler
from ServerAutomata import AUTOMATA, INITIAL_STATE, PLAYING, LOGGED, SAME

MAX_ELAPSED_TIME = 300 # 5 minutes timeout

class Server():
    def __init__(self, port, dbfile = 'db.json', logfile = 'log.txt'):
        self.port = port # port to listen
        self.db = Database(dbfile)
        self.logger = Logger(logfile) 
        self.tcp_socket = NetworkHandler(TCP)
        self.udp_socket = NetworkHandler(UDP)
        self.sockets = []           # all socket interfaces (server + client)
        self.addr_lookup = {}       # addr -> client
        self.username_lookup = {}   # username -> client

    def start(self):
        """
        start and run server
        """

        # bind port
        host = ''
        port = self.port
        self.tcp_socket.bind((host, port))
        self.udp_socket.bind((host, port+1))

        # listen for incoming connections
        self.tcp_socket.listen()

        # log info...
        self.logger.log("server started running")
        self.logger.log(f"listening on port {port} for TCP connections")
        self.logger.log(f"listening on port {port+1} for UDP connections")

        # sockets
        self.sockets = [self.tcp_socket, self.udp_socket]

        self.heartbeat_check()

        # run forever
        while True:
            readable, writable, errorable = select.select(self.sockets, [], [])
            for s in readable:
                if s is self.tcp_socket:
                    self.handle_tcp_socket()
                elif s is self.udp_socket:
                    self.handle_udp_socket()
                elif s.addr in self.addr_lookup:
                    self.handle_client_socket(s)

    def terminate(self):
        self.logger.log(f"server stopped running")
        self.db.update_db()
        clients = [x for x in self.addr_lookup.values()]
        for client in clients:
            self.remove_client(client)
            client.close()

    def heartbeat_check(self):
        self.logger.print('running heartbeat check')

        rightnow = now()
        to_remove_queue = []
        for client in self.addr_lookup.values():
            if rightnow - client.last_seen > MAX_ELAPSED_TIME:
                to_remove_queue.append(client)

        for client in to_remove_queue:
            self.remove_client(client)
            self.logger.log(f"client {client.addr} disconnected due to timeout")
            client.close()

        heartbeat_thread = threading.Timer(MAX_ELAPSED_TIME, self.heartbeat_check)
        heartbeat_thread.start()

    def remove_client(self, client):
        user = client.username
        addr = client.addr
        if user in self.username_lookup:
            self.username_lookup.pop(user)
        if addr in self.addr_lookup:
            self.addr_lookup.pop(addr)

        # only tcp clients are stored in sockets array
        # the udp clients all share the same socket
        if client.socket is not self.udp_socket:
            self.sockets.remove(client)

    def handle_udp_socket(self):
        data = self.udp_socket.recv()
        addr = self.udp_socket.addr
        addrstr = f"{addr[0]}:{addr[1]}"

        if addrstr in self.addr_lookup:
            client = self.addr_lookup[addrstr]
        else:
            client = ClientSocket(self.udp_socket, addr)
            self.addr_lookup[addrstr] = client
            self.logger.log(f'got new UDP connection from {addrstr}')

        self.handle_client_socket(client, data)


    def handle_tcp_socket(self):
        """
        handle a new incoming tcp connection
        """

        # accept incoming request
        socket, addr = self.tcp_socket.accept()

        # client is a wrapper for client sockets 
        client = ClientSocket(socket, addr)

        # log information...
        self.logger.log(f"got new TCP connection from {client.addr}")

        # add client socket to mapping
        self.addr_lookup[client.addr] = client
        self.sockets.append(client)

    def handle_client_socket(self, client, data = None):
        """
        handle already existing connection to client
        """

        # before anything, update client's last seen timestamp
        client.last_seen = now()

        # check for data
        if data == None:
            data = client.recv()

        # if an error occurs, this needs to be logged
        errortype = ''

        # if empty data
        if not data:
            errortype = 'connection closed unexpectedly'

        # else, try decoding it
        try:
            msg = data.decode()
        except UnicodeDecodeError:
            errortype = 'message with invalid characters'

        # error occurred receiving message...
        if errortype != '':
            self.remove_client(client)
            self.logger.log(f'client {client.addr} disconnected abnormally: {errortype}')
            client.close()
            return

        argv = msg.split()
        argc = len(argv)-1
        args = argv[1:]

        # validate message
        if argc == -1:
            client.send('CERR 400\nERRO: comando não providenciado')
            return

        # validate command
        cmd = argv[0]
        if cmd not in AUTOMATA:
            client.send('CERR 400\nERRO: comando inválido')
            return

        # validate cmd formatting
        expected_args = AUTOMATA[cmd]['args']
        if argc != expected_args:
            client.send(f"{cmd} 400\nERRO: comando mal formatado")
            return

        # validate state transition
        current_state = client.state
        possible_incoming_states = AUTOMATA[cmd]['incoming_states']

        if current_state & possible_incoming_states == 0:
            client.send(f'{cmd} 403\nERRO: comando inesperado')
            return

        next_state = AUTOMATA[cmd]['next_state']

        # update state if success
        if self.exec_command(client, cmd, args) and next_state != SAME:
            client.state = next_state

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
            'SADR': self.exec_cmd_sadr,
            'MSTR': self.exec_cmd_mstr,
            'MEND': self.exec_cmd_mend,
            'GBYE': self.exec_cmd_gbye,
            'CPWD': self.exec_cmd_cpwd,
        }

        return cmd2fn[cmd](socket, args)

    def exec_cmd_helo(self, client, args):
        client.send('HELO 200')
        return True

    def exec_cmd_ping(self, client, args):
        client.send('PING 200')
        return True

    def exec_cmd_pinl(self, client, args): 
        client.send(f'PINL 200\n{now()}')
        return True

    def exec_cmd_nusr(self, client, args):
        db = self.db
        username = args[0]
        password = args[1]
        if db.user_exists(username):
            reply = 'NUSR 403\nERRO: usuário já existe'
            success = False
        else:
            db.add_user(username, password)
            reply = 'NUSR 200'
            success = True
        client.send(reply)
        return success

    def exec_cmd_logn(self, client, args):
        db = self.db
        success = False
        username = args[0]
        passwd = args[1]

        # aliases to avoid typing long variable names
        addr = client.addr
        log = self.logger.log

        if not db.user_exists(username):
            reply = 'LOGN 403\nERRO: usuário não existe'
            log(f"failed login attempt from {addr} (user '{username}' does not exist)")
        elif username in self.username_lookup:
            reply = 'LOGN 403\nERRO: usuário já conectado'
            log(f"failed login attempt from {addr} (user '{username}' already connected)")
        elif not db.can_user_log_in(username, passwd):
            reply = 'LOGN 403\nERRO: senha incorreta'
            log(f"failed login attempt from {addr} (wrong password for '{username}')")
        else:
            client.username = username
            self.username_lookup[username] = client
            reply = 'LOGN 200'
            success = True
            log(f"successful login into '{username}' from {addr}")

        client.send(reply)
        return success

    def exec_cmd_lout(self, client, args):
        username = client.username

        if username not in self.username_lookup:
            reply = 'LOUT 403\nERRO: usuário não está logado'
            success = False
        else:
            client.username = ''
            self.username_lookup.pop(username)
            reply = 'LOUT 200'
            success = True

        client.send(reply)
        return success

    def exec_cmd_usrl(self, client, args):
        reply = 'USRL 200'

        # for each connected user, print its name
        for user in self.username_lookup:
            # skip current client
            if user == client.username:
                continue

            # if client is playing, show a marker
            other_client = self.username_lookup[user]
            if other_client.state == PLAYING:
                reply += f"\n{user} *"
            else:
                reply += f"\n{user}"

        client.send(reply)
        return True

    def exec_cmd_uhof(self, client, args):
        reply = 'UHOF 200\n'
        reply += "*** START ***\n"
        reply += self.db.list_users_by_score()
        reply += "***  END  ***"
        client.send(reply)
        return True

    def exec_cmd_gtip(self, client, args):
        user = args[0]
        if user not in self.username_lookup:
            reply = 'GTIP 404\nERRO: usuário não conectado'
            success = False
        else:
            other_client = self.username_lookup[user]
            ip = other_client.ip
            port = other_client.udp_port
            reply = f'GTIP 200\n{ip} {port}'
            success = True
        client.send(reply)
        return success

    def exec_cmd_sadr(self, client, args):
        try:
            client.udp_port = int(args[0])
            client.send('SADR 200')
            return True
        except ValueError:
            client.send('SADR 400\nERRO: comando malformatado')
            return False

    def exec_cmd_cpwd(self, client, args):
        username = client.username
        old = args[0]
        new = args[1]
        db = self.db

        log = self.logger.log

        if not db.user_password_matches(username, old):
            reply = 'CPWD 403\nERRO: senha errada'
            success = False
            log(f"failed attempt to change password for user '{username}' (wrong password)")
        else:
            db.set_user_password(username, new)
            reply = 'CPWD 200'
            success = True
            log(f"successful password change for user '{username}'")
        client.send(reply)
        return success

    def is_playing(self, username):
        client = self.username_lookup[username]
        return client.state == PLAYING

    def exec_cmd_mstr(self, client, args):
        db = self.db
        user_1 = client.username
        user_2 = args[0]
        clients = self.username_lookup
        success = False

        if not (user_1 in clients and user_2 in clients):
            reply = 'MSTR 401\nERRO: usuário não está conectado'
        elif user_1 == user_2:
            reply = 'MSTR 400\nERRO: usuário não pode jogar contra si mesmo'
        elif self.is_playing(user_1) or self.is_playing(user_2):
            reply = 'MSTR 403\nERRO: usuário já está jogando'
        else:
            # record match in database
            matchid = db.start_match(user_1, user_2)

            # update state of connected clients
            # this is hardcoded :-(
            client_1 = clients[user_1]
            client_2 = clients[user_2]
            client_1.state = PLAYING
            client_2.state = PLAYING

            # success!
            reply = f'MSTR 200\n{matchid}'
            success = True

            # log it
            addr_1 = self.username_lookup[user_1].addr
            addr_2 = self.username_lookup[user_2].addr
            self.logger.log(f"new match: <{user_1}> ({addr_1}) VS <{user_2}> ({addr_2})")

        client.send(reply)
        return success

    def exec_cmd_mend(self, client, args):
        db = self.db
        success = False

        try:
            matchid = int(args[0])
        except ValueError:
            client.send('MEND 400\nERRO: comando malformatado')
            return False

        winner = args[1]

        if not db.match_exists(matchid):
            reply = 'MEND 404\nERRO: match não existe'
        elif not db.record_match(matchid, winner):
            reply = 'MEND 403\nERRO: match não pode ser alterado'
        else:
            reply = 'MEND 201'
            success = True

            # hardcoded way to change the state of two users
            username_1, username_2 = db.get_users_from_match(matchid)
            user_1 = self.username_lookup[username_1]
            user_2 = self.username_lookup[username_2]
            user_1.state = user_2.state = LOGGED
            addr_1 = user_1.addr
            addr_2 = user_2.addr
            result = db.get_winner_result(matchid)
            self.logger.log(f'a match has finished: <{username_1}> ({addr_1}) VS <{username_2}> ({addr_2}) [{result}]')

        client.send(reply)
        return success

    def exec_cmd_gbye(self, client, args):
        self.remove_client(client)
        self.logger.log(f'client {client.addr} disconnected')
        client.send('GBYE 200')
        client.close()
        return True


class ClientSocket():
    def __init__(self, socket, addr):
        self.socket = socket
        self.username = ''
        self.state = INITIAL_STATE
        self.ip = addr[0]
        self.port = addr[1]
        self.addr = f"{addr[0]}:{addr[1]}"
        self.udp_port = ''
        self.last_seen = now()

    def fileno(self):
        return self.socket.fileno()

    def recv(self):
        return self.socket.recv(BUFFER_SIZE)

    def send(self, msg):
        #msg += '\n'
        self.socket.send(msg.encode())

    def close(self):
        self.socket.close()

def now():
    return int(time.clock_gettime(0))
