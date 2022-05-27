from os import path
import json

DISCONNECTED = 0
CONNECTED = 1
PLAYING = 2

class Database():
    def __init__(self, userfile_path):
        self.userfile_path = userfile_path

        # if path doesn't exist, we have empty database
        if not path.isfile(userfile_path):
            self.users = {}
            self.matches = []
            pass

        # Otherwise, just load the data
        with open(userfile_path, "r") as f:
            db = json.load(f)
            self.users = db['users']
            self.matches = db['matches']

    def user_exists(self, username):
        return (username in self.users.keys())

    def add_user(self, username, password):
        nusers = len(self.users.keys())
        uid = 1+nusers

        self.users[username] = {
            'id': uid,
            'username': username,
            'password': password,
            'state': DISCONNECTED,
            'wins': 0,
            'losses': 0,
            'ties': 0,
            'last_match_id': -1,
        }

        self.update_db()

    def set_user_password(self, username, password):
        self.users[username] = password
        self.update_db()
        pass

    def connect_user(self, username):
        self.users[username]['state'] = CONNECTED

    def disconnect_user(self, username):
        self.users[username]['state'] = DISCONNECTED

    def disconnect_all_users(self):
        for user in self.users:
            user['state'] = DISCONNECTED
        self.update_db()

    def is_user_playing(self, username):
        return self.users[username]['state'] == PLAYING

    def start_match(self, a, b):
        # mark the users as playing a new game
        self.users[a]['state'] = PLAYING
        self.users[b]['state'] = PLAYING

        # match_id is used to update the correct match after the play
        match_id = len(self.matches)

        # match is (user A, user B, who_won)
        match = [a, b, -1]

        # if who_won == -1, play hasn't finished or wans't finished properly
        # if who_won == 1, player A won
        # if who_won == 2, player B won
        # if who_won == 0, there was a tie

        # ok, so append the match
        self.matches.append(match)

        # match_id is also used to register the last match of user, so we  don't
        # mark the user as not playing IF he started playing with  someone  else
        # before we register this match. Otherwise, the user  would  be  playing
        # another game but we would mark him as not playing because of  lack  of
        # synchronization!

        self.users[a]['last_match_id'] = match_id
        self.users[b]['last_match_id'] = match_id


    def record_match(self, match_id, winner, loser, tie = False):
        
        match = self.matches[match_id]
        if tie:
            match[2] = 0
        elif match[0] == winner:
            match[2] = 1
        else:
            match[2] = 2

        winner = self.users[winner]
        loser = self.users[loser]

        if tie:
            winner['ties'] += 1
            loser['ties'] += 1
        else:
            winner['wins'] += 1
            loser['losses'] += 1

        # mark the user as not playing if he is currently playing  a  game  this
        # match, which was just finished now. If he  is  playing  another  game,
        # then don't mark him as not playing!

        if winner['last_match_id'] == match_id and winner['state'] == PLAYING:
            winner['state'] = CONNECTED
        if loser['last_match_id'] == match_id and loser['state'] == PLAYING:
            loser['state'] = CONNECTED

        self.update_db()

    def list_connected_users(self):
        l = []
        for user in self.users.keys():
            if user['state'] in [ CONNECTED, PLAYING ]:
                displayname = user['username']
                if user['state'] == PLAYING:
                    displayname += " *"
                l.append(displayname)
        return l

    def list_users_by_score(self):
        users = list(self.users.values())
        def calc_score(user):
            return 2*user['wins'] + user['ties'] - user['losses']
        users.sort(key=calc_score)
        return users

    def update_db(self):
        with open(self.userfile_path, "w") as f:
            db = { 'users': self.users, 'matches': self.matches }
            json.dump(db, f)
