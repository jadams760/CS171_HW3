import socket
import threading
import pickle
class Resource:
    def __init__(self, port, ipAddress):
        self.ipAddr = ipAddress
        self.portNum = port
        self.log = []
        self.currentLocker = False
        self.currentQuorum = []
        self.quorumType = ""
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
        messageType = firstMessage[0]
        sender = firstMessage[1]

        if (messageType == 'release'):
            conn.send(pickle.dumps('ack'))
            print("Site%i release %s lock quorum %i, %i, and %i" % (self.currentLocker, self.quorumType, self.currentQuorum[0], self.currentQuorum[1], self.currentQuorum[2]))
            self.currentLocker = False
            self.currentQuorum = []

        elif (messageType == 'append'):
            if (self.currentLocker):
                print ("something real bad happened.")
            self.currentLocker = sender
            self.currentQuorum = firstMessage[2]
            print("Site%i exclusive lock quorum %i, %i, and %i" % (self.currentLocker, self.currentQuorum[0], self.currentQuorum[1], self.currentQuorum[2]))
            logAdd = firstMessage[3]
            self.log.append(logAdd)
            self.quorumType = "exclusive"
            conn.send(pickle.dumps('ack'))

        elif (messageType == 'read'):
            if (self.currentLocker):
                print ("something real bad happened.")
            self.currentLocker = sender
            self.currentQuorum = firstMessage[2]
            print("Site%i shared lock quorum %i, %i, and %i" % (self.currentLocker, self.currentQuorum[0], self.currentQuorum[1], self.currentQuorum[2]))
            self.quorumType = 'shared'
            returnMessage = { 'numMessages': len(self.log) }
            conn.send(pickle.dumps(returnMessage))
            conn.recv(4)
            for i in self.log:
                conn.send(pickle.dumps(i))
                conn.recv(4096)
        conn.close()
        return

if __name__ == '__main__':
    resource = Resource(10000, '172.30.0.73')
    resource.run()

