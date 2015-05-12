# this is our site 'actor'
import threading
import pickle
import re
import os
import socket
import time
import network
from pprint import pprint
class Action:
    DELETE = 1
    POST = 2

class Actor(threading.Thread):
    def __init__(self, instructionFile, outputFile, actorID, actorDirectory, totalActors):
        threading.Thread.__init__(self)
        self.instructionFile = instructionFile
        self.outputFile = outputFile
        self.actorID = actorID
        self.actorDirectory = actorDirectory
        self.timeTable = {}
        self.totalActors = totalActors
        self.log = []
        self.dictionary = {}
        self.lockDict = { 'dictLock': threading.RLock(), 'logLock':threading.RLock(), 'timeTableLock': threading.RLock() }
        for i in range(totalActors):
            self.timeTable[i+1] = {}
            for j in range(totalActors):
                self.timeTable[i+1][j + 1] = 0
        self.network = network.Network(self.actorDirectory[self.actorID], self.log, self.timeTable, self.dictionary, self.totalActors, self.lockDict, self.actorID)

    def run(self):
        self.network.start()
        with open(self.instructionFile, 'r') as instructionHandle, open(self.outputFile, 'w+') as outputFile:
            actionReturn = self.act(instructionHandle)
            while actionReturn != False:
                outputFile.write(actionReturn + "\n")
                self.garbageCollect()
                actionReturn = self.act(instructionHandle)
            # Chop off the last space
            #outputFile.seek(-1, os.SEEK_END)
            #outputFile.truncate()

    # given a file object, we'll check the next command to be executed and do so.
    def act(self, fileObj):
        line = fileObj.readline()[:-1].split(None, 2)
        if (line == []):
            return False
        command = line[0]
        if (command == 'Post'):
            with self.lockDict['logLock'], self.lockDict['timeTableLock'], self.lockDict['dictLock']:
                self.log.append((Action.POST, self.actorID, self.timeTable[self.actorID][self.actorID] + 1, line[1], line[2]))
                self.dictionary[int(line[1])] = line[2]
                self.timeTable[self.actorID][self.actorID] += 1
            return "Post %i" % int(line[1])
        elif (command == 'Delete'):
            if int(line[1]) not in self.dictionary:
                return "Delete %i failed" % int(line[1])
            else:
                with self.lockDict['logLock'], self.lockDict['timeTableLock']:
                    self.log.append((Action.DELETE, self.actorID, self.timeTable[self.actorID][self.actorID] + 1, line[1]))
                    del self.dictionary[int(line[1])]
                    self.timeTable[self.actorID][self.actorID] += 1
                return "Delete %i" % int(line[1])
        elif (command == 'Share'):
            # We are going to send p + 1 messages from i to j, where p is the sum of: for k <= n TimeTable[i][k] - TimeTable[j][k]. Our first message will tell how large p is and also contains our timetable
            # We first filter our log and make a new log with all events that our destination actor might not know about.
            destActor = int(line[1])
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverAddress = ('localhost', self.actorDirectory[destActor])
            sock.connect(serverAddress)
            # First we send our initial message, then p additional messages. We wait for an 'ack' for each message except the initial.
            with self.lockDict['timeTableLock'], self.lockDict['logLock'], self.lockDict['dictLock']:
                sendList = filter(lambda q: q[2] > self.timeTable[destActor][q[1]], self.log)
                numEvents = len(sendList)
                transmit = pickle.dumps( {'numEvents':numEvents, 'timeTable':self.timeTable, 'sourceActor':self.actorID } )

                sock.send(transmit)
                sock.recv(20)
                for i in range(numEvents):
                    toSend = pickle.dumps(sendList[i])
                    sock.send(toSend)
                    sock.recv(20)
                sock.close()
            return "Share %i" % destActor
        elif (command == "Idle"):
            time.sleep(int(line[1]))
            return "Idle %i seconds" % int(line[1])
        elif (command == "ShowBlog"):
            ret = "Blog: "
            with self.lockDict['dictLock']:
                for i in self.dictionary:
                    ret += "%i," % i
            return ret[:-1]
        elif (command == "PrintState"):
            with self.lockDict['timeTableLock'], self.lockDict['logLock']:
                ret = "Log: {"
                for i in self.log:
                    if i[0] == Action.DELETE:
                        action = "delete"
                        ret += "%s(%i)," % (action, int(i[3]))
                    elif i[0] == Action.POST:
                        action = "post"
                        ret += "%s(%i,\"%s\")," % (action, int(i[3]), i[4])
                ret = ret[:-1]
                ret += "}\nTimeTable:\n"
                for i in range(self.totalActors):
                    ret += "|  "
                    for j in range(self.totalActors):
                        ret += "%i  " % self.timeTable[i + 1][j + 1]
                    ret = ret[:-2]
                    ret += "|\n"
                ret = ret[:-1]
                return ret
        else:
            print "Command not recognized: " + command
            return False
    def garbageCollect(self):
        # here we filter our list for any elements that have times greater than the minimum of the TimeTable where the column is the actorID the event occured on
        # this line in english:
        # include any elements where not all values of the column timeTable[y][element_site] are greater than or equal to the element's time
        with self.lockDict['logLock']:
            for i in self.log:
                if all([ self.timeTable[y + 1][i[1]] >= i[2] for y in range(self.totalActors)]):
                    self.log.remove(i)
        return

