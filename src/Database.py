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
        }

        self.update_db()

    def set_user_password(self, username, password):
        self.users[username] = password
        self.update_db()
        pass

    def can_user_log_in(self, username, password):
        return self.users[username]['password'] == password

    def start_match(self, a, b):
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

        #
        return match_id

    def match_exists(self, match_id):
        return match_id < len(self.matches)

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

        self.update_db()

    def list_users_by_score(self):
        users = list(self.users.values())
        def calc_score(user):
            return 2*user['wins'] + user['ties'] - user['losses']
        users.sort(key=calc_score)

        score_list = ''
        for user in users:
            score = calc_score(user)
            name = user['username']
            score_list += f'{name}\t{score}\n'
        return score_list

    def update_db(self):
        with open(self.userfile_path, "w") as f:
            db = { 'users': self.users, 'matches': self.matches }
            json.dump(db, f)
