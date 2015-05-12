# This is our network 'sub-thread'.
import threading
import socket
import pickle
import time
import sys
from pprint import pprint

class Action:
    DELETE = 1
    POST = 2

class Network(threading.Thread):
    def __init__(self, port, actorLog, actorTable, actorDict, totalActors, actorID):
        threading.Thread.__init__(self)
        self.portNum = port
        self.ipAddr = 'localhost'
        # treat the network as a daemon
        self.daemon = True
        self.actorLog = actorLog
        self.actorDict = actorDict
        self.actorTable = actorTable
        self.transmissions = 0
        self.totalActors = totalActors
        self.actorID = actorID
        self.isRequesting = False
        self.activeLocksLock = threading.RLock()
        self.requestedLocksLock = threading.RLock()
        self.activeLocks = []
        self.requestedLocks = []

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverAddress = (self.ipAddr, self.portNum)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(serverAddress)
        sock.listen(1)
        while 1:
            conn, addr = sock.accept()
            thread = threading.Thread(target=self.handle,args=(conn,))
            thread.start()

    def handle(self, conn):
        message = pickle.loads(conn.recv(4092))
        conn.send("ack")
        messageType = message[0]
        sender = message[1]
        ## We can have two types of locks, reads and writes. We handle both here.
        if (messageType == 'lock'):
            lockType = message[2]

            if (lockType == 'write'):
                ## We are going to keep checking until we have no active locks to send the grant.
                lockDict = { 'sender':sender, 'type':lockType }
                with requestedLocksLock:
                    requestedLocks.append(lockDict)
                ## Loop until there are no activeLocks and we're next up, we send a grant.
                while True:
                    with requestedLocksLock, activeLocksLock:
                        if not activeLocks and (requestedLocks[0] == lockDict):
                            activeLocks.append(lockDict)
                            break
                conn.send("grant")
                conn.close()

            elif (lockType == 'read'):
                lockDict = { 'sender':sender, 'type':lockType }
                with requestedLocksLock:
                    requestedLocks.append(lockDict)
                ## Loop until there are no activeLocks and we're next up OR there is an activeLock, but it's a read.
                while True:
                    with requestedLocksLock, activeLocksLock:
                        if (not activeLocks and (requestedLocks[0] == lockDict)) or (activeLocks and activeLocks[0]['type'] == 'read'):
                            activeLocks.append(lockDict)
                            break
                conn.send("grant")

        elif (messageType == 'release'):
            with activeLocksLock:
                activeLocks = list(filter(lambda lock: lock['sender'] != sender, activeLocks))
            conn.send("ack")
        conn.close()
        return


