import threading
from threading import Thread
import types
import socket
import time
import array
import pickle
import sys
import random

x = 0
HOSTNAME = "localhost"
PORT = 9990


LOGHOST = "localhost"
LOGPORT = 9999

locks = ['','','','','']
sites = [] ##(siteID, HOSTNAME, PORT)
quorum = []

def myConnect(socket,host,port):
    while True: ## send message to log
        try:
            socket.connect(host,port)
            break
        except:
            continue
        
def mySend(socket,send):
    socket.send(pickle.dumps(send))
    
def myReceive(socket):
    while True: ## send message to log
        try:
            receive = socket.recv(4096)
            break
        except:
            continue
    return pickle.loads(receive)
        
def CLI(siteID):
    while True:
        print("Please Enter One of the Following and Press Enter:\n(1) Read\n(2) Append\n(3) Exit")
        x = input()
        if x == "1":
            print("read")
            while len(quorum) < 2:  ## set up quorum
                qSite = random.choice(sites)
                if qSite[0] == siteID:
                    continue
                elif qSite in quorum:
                    continue
                else:
                    quorum.append(qSite)
                    
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            myConnect(s,quorum[0][1], quorum[0][2])
            send = ["Read", siteID]
            mySend(send)
            message = myReceive(s)
            if message == "GrantRead":
                continue
            else:
                print("Incorrect Grant Message\n")
                break
            
            myConnect(s,quorum[1][1], quorum[1][2])
            send = ["Read", siteID]
            mySend(send)
            message = myReceive(s)
            if message == "GrantRead":
                continue
            else:
                print("Incorrect Grant Message\n")
                break


            while 'w' in locks: ## check if there are any active write locks
                continue

            myConnect(s,LOGHOST, LOGPORT)
            send = ["Read", quorum[0][0], quorum[1][0], siteID]
            mySend(send)
            message = myReceive(s)
            print(message)

            myConnect(s,LOGHOST, LOGPORT)
            send = ["Release",siteID]
            mySend(send)
            message = myReceive(s)
            if message == "Acknowledge":
                continue
            else:
                print("No Acknowledgement Received\n")
                break
            

            myConnect(s,quorum[0][1], quorum[0][2])
            send = ["Release", siteID]
            mySend(send)
            s.close()
            

            myConnect(s,quorum[1][1], quorum[1][2])
            mySend(send)
            s.close()
            

                
        elif x == "2":
            print("append")

            
        elif x == "3":
            print("exit")
            sys.exit(1)

            
        else:
            continue

def Comm(siteID):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    uniquePort = PORT + siteID
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((HOSTNAME, uniquePort))
    serverSocket.listen(5)


    while True:
        
        (comSocket, address) = serverSocket.accept()
        receive = myReceive(comSocket)
        
        if receive[0] == "Read":
            while "w" in locks:
                continue
            locks[siteID-1] = "r"
            mySend(comSocket,"GrantRead")
            receive = myReceive(comSocket)
            if receive[0] = "Release":
                locks[receive[1]-1] = ''
            else:
                print("No Release\n")
                break

        elif
            











    
