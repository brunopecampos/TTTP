# TTTP
TTTP stands for TikTakToe Protocol. It is a pseudo P2P protocol used as a for 
playing tiktaktoe. It has two entities, a client and a server. The server has
all the player's scores and has a log-in system. The match is played among two
clients, without server intervention.

Contributors
- Bruno Pereira Campos
- André Souza Abreu


# Project Structure

- src/: source code
- data/: where the database (db.json), log file (log.txt) and some static files 
- (other JSON files) are stored
- slide.pdf: the project presentation
- Makefile: rules to compile project

# Executing

It is necessary to have python installed (version 3.10.4 is preferred), as well 
as the following libraries: threading, time, datetime, os, json, select.

## Server

To run the server, execute:

```shell
make runserver
```

The server will start listening to TCP connections in port 5000 and UDP 
connections at port 5001.

## Rodando o cliente

To run the Client, execute:

```shell
./src/Client.py <SERVER IP> <SERVER PORT> <PUBLIC PORT>
```

'SERVER IP' is the IP address of the server, 'SERVER  PORT' is the server port,
'PUBLIC PORT' is the port in which the client will receive connection from other 
clients during a match, 'TYPE OF CONNECTION' is the type of connection, '-t' for
TCP and '-u' for UDP. Arguments must be put in the order shown.

For example, to connection to the server running at localhost and use port 7000
for other client connection, execute:

```shell
./src/Client.py 127.0.0.1 5000 7000
```

Alternatively, you canexecute the commands `make  runclient1`  and  `make
runclient2`,  to run the client in port 7000 and 7001. This assumes that
the server ip is 127.0.1 and it is available at 5000 port.
