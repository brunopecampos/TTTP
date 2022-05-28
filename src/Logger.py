class Logger():
    def __init__(self, filepath = 'logs.log'):
        self.filepath = filepath
        self.file = open(filepath, "w")

    def log(self, text):
        self.file.write(text)

    def close(self):
        self.file.close()
