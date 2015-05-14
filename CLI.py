# this is our site 'actor'
import threading
import pickle
import re
import os
import socket
import time
import random
import network
from pprint import pprint

localhost = "localhost"
sites = [(1,'52.7.152.215',10000), (2,'54.94.193.66',10000), (3,'52.74.189.123',10000), (4,'52.74.190.114',10000),(5,'52.74.160.204',10000)]

class CLI(threading.Thread):
    def __init__(self, siteID, sites, hostname, port):
        threading.Thread.__init__(self)
        self.siteID = siteID
        self.hostname = hostname
        self.port = port
        self.sites = sites
        self.network = network.Network(self.port,len(sites),self.siteID)
        self.logHost = '52.74.189.66'
        self.logPort = 10000
    def myConnect(self,socket,host,port):
        socket.connect((host,port))

    def mySend(self,sock,send):
        sock.send(pickle.dumps(send))

    def myReceive(self,socket):
        receive = socket.recv(4096)
        return pickle.loads(receive)
    def run(self):
        self.network.start()
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            userInput = input("Please Enter One of the Following and Press Enter:\n(1) Read\n(2) Append\n(3) Exit\n")
            if userInput == "1":
##                print("Read\n")
                quorum = []
                quorum.append((self.siteID,localhost,9990+self.siteID))
                while len(quorum) < 3:
                    qSite = random.choice(self.sites)
                    if int(qSite[0]) == self.siteID:
                        continue
                    elif qSite not in quorum:
                        quorum.append(qSite)
                    else:
                        continue

                self.myConnect(sock,self.hostname,self.port)
                send = ["lock", self.siteID, "read"]
                self.mySend(sock,send)
                receive = self.myReceive(sock)
##                if receive == "grant":
##                    print("grant")
##
##                else:
####                    print("not grant")
####                    print("received %s" % receive)
##                    return False
                sock.close()

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,quorum[0][1], quorum[0][2])
                send = ["lock", self.siteID, "read"]
                self.mySend(sock,send)
                receive = self.myReceive(sock)
##                if receive == "grant":
##                    print("grant")
##
##                else:
##                    print("not grant")
##                    return False
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                self.myConnect(sock,quorum[1][1], quorum[1][2])
                send = ["lock", self.siteID, "read"]
                self.mySend(sock,send)
##                receive = self.myReceive(sock)
##                if receive == "grant":
##                    print("grant")
##
##                else:
##                    print("not grant")
##                    return False
                sock.close()

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                self.myConnect(sock,self.logHost,self.logPort) ##send "read" to log and print response
                qList = [quorum[0][0],quorum[1][0],quorum[2][0]]
                send = ["read", self.siteID, qList]
                self.mySend(sock,send)
                receive = self.myReceive(sock)
                numMessages = int(receive['numMessages'])
##                print("Read Success("+ str(numMessages) +" items to receive):")
                send = ["ack"]
                self.mySend(sock,send)
                print("\n")
                for i in range(numMessages):
                    receive = self.myReceive(sock)
                    print(receive)
                    send = ["ack"]
                    self.mySend(sock,send)
                print("\n")
                sock.close()

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


                self.myConnect(sock,self.logHost,self.logPort) ##send "read" to log and print response

                send = ["release", self.siteID]
                self.mySend(sock,send)
                receive = self.myReceive(sock)
##                print(receive)
                sock.close()

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                self.myConnect(sock,quorum[0][1], quorum[0][2]) ##send "release" to qSite1 and
                "ack"
                self.mySend(sock,send)
                sock.close() ##close since no response needed after release

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,quorum[1][1], quorum[1][2]) ##send "release" to qSite2 and print "ack"
                self.mySend(sock,send)
                sock.close() ##close since no response needed after release



            elif userInput == "2":
                userInput = input("Please enter a message to append:\n")
                userInput = userInput[:140]

                quorum = []
                quorum.append((self.siteID,localhost,9990+self.siteID))
                while len(quorum) < 3:
                    qSite = random.choice(self.sites)
                    if int(qSite[0]) == self.siteID:
                        continue
                    elif qSite not in quorum:
                        quorum.append(qSite)
                    else:
                        continue
##                print(quorum)
                self.myConnect(sock,self.hostname,self.port)
                send = ["lock", self.siteID, "write"]
                self.mySend(sock,send)

                receive = self.myReceive(sock)

##                if receive == "grant":
##                    print("grant")
##
##                else:
##                    print("not grant")
##                    return False
                sock.close()

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,quorum[1][1], quorum[1][2])
                send = ["lock", self.siteID, "write"]
                self.mySend(sock,send)
                receive = self.myReceive(sock)

##                if receive == "grant":
##                    print("grant")
##
##                else:
##                    print("not grant")
##                    return False
                sock.close()

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,quorum[2][1], quorum[2][2])
                send = ["lock", self.siteID, "write"]
                self.mySend(sock,send)
                receive = self.myReceive(sock)
##                if receive == "grant":
##                    print("grant")
##
##                else:
##                    print("not grant")
##                    return False
                sock.close()

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,self.logHost,self.logPort) ##send "append" to log and print ack
                qList = [quorum[0][0],quorum[1][0],quorum[2][0]]
                send = ["append", self.siteID, qList,userInput]
                self.mySend(sock,send)
                receive = self.myReceive(sock)
##                print(receive + " from append resource")
                sock.close()

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,self.logHost,self.logPort)
                send = ["release",self.siteID]
                self.mySend(sock,send)
                receive = self.myReceive(sock)
##                print(receive + " from release resource")
                sock.close()

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,quorum[0][1], quorum[0][2]) ##send "release" to qSite1
                self.mySend(sock,send)
                sock.close() ##close since no response needed after release

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,quorum[1][1], quorum[1][2]) ##send "release" to qSite2
                self.mySend(sock,send)
                sock.close() ##close since no response needed after release

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,quorum[2][1], quorum[2][2]) ##send "release" to qSite2
                self.mySend(sock,send)
                sock.close() ##close since no response needed after release

            elif userInput == "3":
                print("Exit\n")
                return False

            else:
                print("Incorrect input type\n")







