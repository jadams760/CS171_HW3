# This is our network 'sub-thread'.
import threading
import socket
import pickle
import time
import sys
from pprint import pprint

class Network(threading.Thread):
    def __init__(self, port, totalActors, actorID, lockEvent, siteDirectory, requestID, ipAddr):
        threading.Thread.__init__(self)
        self.portNum = port
        self.ipAddr = ipAddr
        # treat the network as a daemon
        self.daemon = True
        self.totalActors = totalActors
        self.actorID = actorID
        self.activeLocksLock = threading.RLock()
        self.requestedLocksLock = threading.RLock()
        self.grantLock = threading.RLock()
        self.activeLocks = []
        self.requestedLocks = []
        self.lockEvent = lockEvent
        self.siteDirectory = siteDirectory
        self.numGranted = 0
        self.requestID = requestID

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
    def clearGrants(self):
        self.numGranted = 0

    def handle(self, conn):
        message = pickle.loads(conn.recv(4092))
        conn.close()
        messageType = message[0]
        sender = message[1]
        senderInfo = list(filter(lambda x: x[0] == sender, self.siteDirectory))[0]
        ## We can have two types of locks, reads and writes. We handle both here.
        if (messageType == 'lock'):
            lockType = message[2]
            requestID = message[3]
            if (lockType == 'write'):
                ## We are going to keep checking until we have no active locks to send the grant.
                lockDict = { 'sender':sender, 'type':lockType }
                with self.requestedLocksLock:
                    self.requestedLocks.append(lockDict)
                ## Loop until there are no self.activeLocks and we're next up, we send a grant.
                while lockDict in self.requestedLocks:
                    with self.requestedLocksLock, self.activeLocksLock:
                        if not self.activeLocks and lockDict in self.requestedLocks and (self.requestedLocks[0] == lockDict):
                            self.activeLocks.append(lockDict)
                            self.requestedLocks.remove(lockDict)
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.connect((senderInfo[1],senderInfo[2]))
                            sock.send(pickle.dumps(['grant', self.actorID, requestID]))
                            sock.close()
                            break



            elif (lockType == 'read'):
                lockDict = { 'sender':sender, 'type':lockType }

                with self.requestedLocksLock:
                    self.requestedLocks.append(lockDict)
                ## Loop until there are no self.activeLocks and we're next up OR there is an activeLock, but it's a read.
                while lockDict in self.requestedLocks:
                    with self.requestedLocksLock, self.activeLocksLock:
                        if (lockDict in self.requestedLocks and not self.activeLocks and (self.requestedLocks[0] == lockDict)) or (lockDict in self.RequestedLocks and self.activeLocks and self.activeLocks[0]['type'] == 'read'):
                            self.activeLocks.append(lockDict)
                            self.requestedLocks.remove(lockDict)
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.connect((senderInfo[1],senderInfo[2]))
                            sock.send(pickle.dumps(['grant', self.actorID, requestID]))
                            sock.close()
                            break
        elif (messageType == 'release'):
            with self.activeLocksLock:
                self.activeLocks = list(filter(lambda lock: lock['sender'] != sender, self.activeLocks))
        elif (messageType == 'grant'):
            pprint(message)
            print("Self.RequestID: %i, self.numGranted: %i" %( self.requestID['requestID'], self.numGranted))
            requestID = message[2]
            ## Ignore any requests that are not our current request ID.
            if (requestID['requestID'] != self.requestID['requestID']):
                return
            with self.grantLock:
                self.numGranted += 1
                if (self.numGranted >= 3):
                    self.lockEvent.set()
                    self.lockEvent.clear()
        elif (messageType == 'nevermind'):
            print("nevermind received")
            with self.requestedLocksLock, self.activeLocksLock:
                self.requestedLocks = list(filter(lambda lock: lock['sender'] != sender, self.activeLocks))
                self.activeLocks = list(filter(lambda lock: lock['sender'] != sender, self.activeLocks))



        return


