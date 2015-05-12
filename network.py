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
    def __init__(self, port, actorLog, actorTable, actorDict, totalActors, lockDict, actorID):
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
        self.lockDict = lockDict
        self.actorID = actorID

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
        firstMessage = pickle.loads(conn.recv(8192))
        conn.send("ack")
        newList = []
        for i in range(firstMessage['numEvents']):
            data = conn.recv(8192)
            newList.append(pickle.loads(data))
            conn.send("ack")
        self.logMerge(newList)
        self.timetableMerge(firstMessage['timeTable'], firstMessage['sourceActor'])
        conn.close()
        return


    def logMerge(self, mergeLog):
        # Merge the two, remove duplicates. Then update our dictionary.
        seen = set()
        seen_add = seen.add
        with self.lockDict['logLock']:
            old = set(self.actorLog)
            for i in mergeLog:
                if i not in self.actorLog:
                    self.actorLog.append(i)
        toUpdate = [x for x in mergeLog if x not in old]
        with self.lockDict['dictLock']:
            for i in toUpdate:
                action = i[0]
                if (action == Action.POST):
                    postID = int(i[3])
                    postMessage = i[4]
                    self.actorDict[postID] = postMessage
                elif(action == Action.DELETE):
                    postID = int(i[3])
                    self.actorDict.pop(postID, None)
        return
    def timetableMerge(self, newTimeTable, sourceActor):
        # first we take the max of all elements. Then we update our own row with the max of our own row and their row.
        with self.lockDict['timeTableLock']:
            for i in range(self.totalActors):
                for j in range(self.totalActors):
                    self.actorTable[i + 1][j + 1] = max(self.actorTable[i + 1][j + 1], newTimeTable[i + 1][j + 1])

            for i in range(self.totalActors):
                self.actorTable[self.actorID][i + 1] = max(self.actorTable[self.actorID][i + 1], newTimeTable[sourceActor][i + 1])
            return

