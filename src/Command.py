class Command():
    def __init__(self, label, next_state):
        self.label = label
        self.next_state = next_state

    def execute(self, client):
        pass