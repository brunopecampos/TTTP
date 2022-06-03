import time

class Logger():
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = open(filepath, "a")

    def log(self, text):
        """
        log text to file and print it to stdout
        """
        output = f'{timeprefix()} {text}\n'
        print(output, end="")
        self.file.write(output)

    def print(self, text):
        """
        print formatted text to stdout
        """
        print(f'{timeprefix()} {text}')

    def close(self):
        """
        close log file
        """
        self.file.close()

def timeprefix():
    t = time.localtime()
    year = t.tm_year
    month = t.tm_mon
    day = t.tm_mday
    hour = t.tm_hour
    min = t.tm_min
    sec = t.tm_sec
    return '[%d-%02d-%02d %02d:%02d:%02d]' % (year, month, day, hour, min, sec)
