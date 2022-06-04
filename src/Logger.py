import time

class Logger():
    def __init__(self, filepath):
        self.filepath = filepath

    def log(self, text):
        """
        log text to file and print it to stdout
        """
        output = f'{timeprefix()} {text}\n'
        print(output, end="")
        self.file = open(self.filepath, "a")
        self.file.write(output)
        self.file.close()

    def print(self, text):
        """
        print formatted text to stdout
        """
        print(f'{timeprefix()} {text}')

def timeprefix():
    t = time.localtime()
    year = t.tm_year
    month = t.tm_mon
    day = t.tm_mday
    hour = t.tm_hour
    min = t.tm_min
    sec = t.tm_sec
    return '[%d-%02d-%02d %02d:%02d:%02d]' % (year, month, day, hour, min, sec)
