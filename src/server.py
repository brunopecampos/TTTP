#!/usr/bin/python3
from Server import Server

port = 5000
dbfile = '../data/db.json'
logfile = '../data/log.txt'
Server(port, dbfile, logfile).start()
