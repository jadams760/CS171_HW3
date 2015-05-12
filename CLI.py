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
sites = [(1,'localhost',9991), (2,'localhost',9992), (3,'localhost',9993), (4,'localhost',9994),(5,'localhost',9995)]

class CLI(threading.Thread):
    def __init__(self, siteID, sites, hostname, port, LogHost, LogPort):
        threading.Thread.__init__(self)
        self.siteID = siteID
        self.hostname = hostname
        self.port = port
        self.sites = sites
        self.network = network.Network(self.port,len(sites),self.siteID)
    def myConnect(self,socket,host,port):
        socket.connect((host,port))

    def mySend(self,socket,send):
        socket.send(pickle.dumps(send))

    def myReceive(self,socket):
        receive = socket.recv(4096)
        return pickle.loads(receive)
    def run(self):
        self.network.start()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            userInput = input("Please Enter One of the Following and Press Enter:\n(1) Read\n(2) Append\n(3) Exit\n")
            if userInput == "1":
                print("Read\n")
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
                if receive == "grant":
                    print("grant")

                else:
                    print("not grant")
                    print("received %s" % receive)
                    return False

                self.myConnect(sock,quorum[0][1], quorum[0][2])
                send = ["lock", self.siteID, "read"]
                self.mySend(sock,send)
                receive = self.myReceive(sock)
                if receive == "grant":
                    print("grant")

                else:
                    print("not grant")
                    return False

                self.myConnect(sock,quorum[1][1], quorum[1][2])
                send = ["lock", self.siteID, "read"]
                self.mySend(sock,send)
                receive = self.myReceive(sock)
                if receive == "grant":
                    print("grant")

                else:
                    print("not grant")
                    return False


                self.myConnect(sock,LogHost,LogPort) ##send "read" to log and print response
                qList = [quoum[0][0],quoum[1][0],quoum[2][0]]
                send = ["read", qList]
                self.mySend(socket,send)
                receive = myReceive(sock)
                print("Read Success("+int(receive)+" items to receive):")
                send = ["ack", self.siteID]
                self.mySend(sock,send)
                for i in range(int(receive)):
                    receive = myReceive(sock)
                    print(receive)
                    send = ["ack", self.siteID]
                    self.mySend(sock,send)



                send = ["release", self.siteID]
                self.myConnect(sock,LogHost,LogPort) ##send "release" to Log and print "ack"
                self.mySend(sock,send)
                receive = myReceive(sock)
                print(receive)

                self.myConnect(sock,quorum[0][1], quorum[0][2]) ##send "release" to qSite1 and print "ack"
                self.mySend(sock,send)
                sock.close() ##close since no response needed after release

                self.myConnect(sock,quorum[1][1], quorum[1][2]) ##send "release" to qSite2 and print "ack"
                self.mySend(sock,send)
                sock.close() ##close since no response needed after release



            elif userInput == "2":
                userInput = input("Please enter a message to append:\n")
                userInput = userInput[:140]
                print("Append " + userInput + "\n")

            elif userInput == "3":
                print("Exit\n")
                return False

            else:
                print("Incorrect input type\n")


def main():

    t = CLI(1,sites,'localhost',9001,'localhost',9999)
    t.start()

if __name__ == "__main__":
    main()






