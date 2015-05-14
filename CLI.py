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


class CLI(threading.Thread):
    def __init__(self, siteID, hostname, port, sites, logHost, logPort):
        threading.Thread.__init__(self)
        self.siteID = siteID
        self.hostname = hostname
        self.port = port
        self.sites = sites
        self.reqDict = {"requestID":0}
        self.event = threading.Event()
        self.network = network.Network(self.port,len(self.sites),self.siteID,self.event,self.sites,self.reqDict, self.hostname)
        self.logHost = logHost
        self.logPort = logPort
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

            userInput = input("Please Enter One of the Following and Press Enter:\n(1) Read\n(2) Append\n(3) Exit\n")
            if userInput == "1":
##                print("Read\n")
                while True:
                    quorum = []
                    quorum.append((self.siteID,self.sites[self.siteID-1][1],self.sites[self.siteID-1][2]))
                    while len(quorum) < 3:
                        qSite = random.choice(self.sites)
                        if int(qSite[0]) == self.siteID:
                            continue
                        elif qSite not in quorum:
                            quorum.append(qSite)
                        else:
                            continue
                    ##connect to quorum sites for "read"

                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.myConnect(sock,quorum[0][1], quorum[0][2]) ##send "lock" for "read" to qSite1
                    send = ["lock", self.siteID, "read",self.reqDict]
                    self.mySend(sock,send)
                    sock.close()

                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.myConnect(sock,quorum[1][1], quorum[1][2]) ##send "lock" for "read" to qSite2
                    send = ["lock", self.siteID, "read",self.reqDict]
                    self.mySend(sock,send)
                    sock.close()

                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.myConnect(sock,quorum[2][1], quorum[2][2]) ##send "lock" for "read" to qSite3
                    send = ["lock", self.siteID, "read",self.reqDict]
                    self.mySend(sock,send)
                    sock.close()



                    if self.event.wait(1):
                        self.reqDict["requestID"] = self.reqDict["requestID"] + 1 ##increment local requestID

                        self.network.clearGrants() ##clear all collected grants on network thread
                        break

                    else:

                        self.reqDict["requestID"] = self.reqDict["requestID"] + 1 ##increment local requestID

                        ##timeout after no notification of grant
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.myConnect(sock,quorum[0][1], quorum[0][2]) ##send "nevermind" to qSite1
                        send = ["nevermind", self.siteID]
                        self.mySend(sock,send)
                        sock.close()


                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.myConnect(sock,quorum[1][1], quorum[1][2]) ##send "nevermind" to qSite2
                        send = ["nevermind", self.siteID]
                        self.mySend(sock,send)
                        sock.close()


                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.myConnect(sock,quorum[2][1], quorum[2][2]) ##send "nevermind" to qSite3
                        send = ["nevermind", self.siteID]
                        self.mySend(sock,send)
                        sock.close()

                        self.network.clearGrants() ##clear all collected grants on network thread



                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,self.logHost,self.logPort) ##send "read" to log and print response
                qList = [quorum[0][0],quorum[1][0],quorum[2][0]]
                send = ["read", self.siteID, qList]
                self.mySend(sock,send)
                receive = self.myReceive(sock)
                numMessages = int(receive['numMessages'])
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


                send = ["release", self.siteID] ##message to send for "release"

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,self.logHost,self.logPort) ##send "release" to log
                self.mySend(sock,send)
                receive = self.myReceive(sock)
                sock.close()


                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,quorum[0][1], quorum[0][2]) ##send "release" to qSite1
                self.mySend(sock,send)
                sock.close()


                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,quorum[1][1], quorum[1][2]) ##send "release" to qSite2
                self.mySend(sock,send)
                sock.close()


                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,quorum[2][1], quorum[2][2]) ##send "release" to qSite3
                self.mySend(sock,send)
                sock.close()



            elif userInput == "2":
                userInput = input("Please enter a message to append:\n")
                userInput = userInput[:140]
                while True:

                    quorum = []
                    quorum.append((self.siteID,self.sites[self.siteID-1][1],self.sites[self.siteID-1][2]))
                    while len(quorum) < 3:
                        qSite = random.choice(self.sites)
                        if int(qSite[0]) == self.siteID:
                            continue
                        elif qSite not in quorum:
                            quorum.append(qSite)
                        else:
                            continue
     ##connect to quorum sites for "append"

                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.myConnect(sock,quorum[0][1], quorum[0][2]) ##send "lock" for "write" to qSite1
                    send = ["lock", self.siteID, "write",self.reqDict]
                    self.mySend(sock,send)
                    sock.close()

                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.myConnect(sock,quorum[1][1], quorum[1][2]) ##send "lock" for "write" to qSite1
                    send = ["lock", self.siteID, "write",self.reqDict]
                    self.mySend(sock,send)
                    sock.close()

                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.myConnect(sock,quorum[2][1], quorum[2][2]) ##send "lock" for "write" to qSite1
                    send = ["lock", self.siteID, "write",self.reqDict]
                    self.mySend(sock,send)
                    sock.close()




                    if self.event.wait(1):
                        ##notify received all sites grant read
                        self.reqDict["requestID"] = self.reqDict["requestID"] + 1 ##increment local requestID
                        self.network.clearGrants() ##clear all collected grants on network thread
                        break

                    else:
                        ##timeout after no notification of grant
                        self.reqDict["requestID"] = self.reqDict["requestID"] + 1 ##increment local requestID
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.myConnect(sock,quorum[0][1], quorum[0][2]) ##send "nevermind" to qSite1
                        send = ["nevermind", self.siteID]
                        self.mySend(sock,send)
                        sock.close()

                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.myConnect(sock,quorum[1][1], quorum[1][2]) ##send "nevermind" to qSite2
                        send = ["nevermind", self.siteID]
                        self.mySend(sock,send)
                        sock.close()

                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.myConnect(sock,quorum[2][1], quorum[2][2]) ##send "nevermind" to qSite3
                        send = ["nevermind", self.siteID]
                        self.mySend(sock,send)
                        sock.close()

                        self.network.clearGrants() ##clear all collected grants on network thread


                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,self.logHost,self.logPort) ##send "append" to log and print ack
                qList = [quorum[0][0],quorum[1][0],quorum[2][0]]
                send = ["append", self.siteID, qList,userInput]
                self.mySend(sock,send)
                receive = self.myReceive(sock)
                sock.close()

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,self.logHost,self.logPort)
                send = ["release",self.siteID]
                self.mySend(sock,send)
                receive = self.myReceive(sock)
                sock.close()

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,quorum[0][1], quorum[0][2]) ##send "release" to qSite1
                self.mySend(sock,send)
                sock.close()

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,quorum[1][1], quorum[1][2]) ##send "release" to qSite2
                self.mySend(sock,send)
                sock.close()

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.myConnect(sock,quorum[2][1], quorum[2][2]) ##send "release" to qSite3
                self.mySend(sock,send)
                sock.close()

            elif userInput == "3":
                return False

            else:
                print("Incorrect input type\n")


