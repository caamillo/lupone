from Game.Util.colors import bcolors as bc
import os
import socket
import threading
import ansicon
import time

class Client:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.username = input(bc().wColors['okblue']+'Coem ti chiami...... '+bc().reset)
        self.connected=False
        self.reconnect=False
        self.createConnection()

    def createConnection(self):
        connection = threading.Thread(target=self.connection,args=())
        connection.start()
        messageHandler = threading.Thread(target=self.handleMessages,args=())
        messageHandler.start()
        inputHandler = threading.Thread(target=self.inputHandler,args=())
        inputHandler.start()
        reconnectAnim = threading.Thread(target=self.reconnectAnim,args=())
        reconnectAnim.start()

    def handleMessages(self):
        while True:
            while self.connected:
                try:
                    msg=self.s.recv(1204).decode()
                    if msg.strip()[0]=='/':
                        args=msg.strip().split()[1:]
                        if len(args)>0:
                            com = msg.strip()[1:msg.strip().find(' ')].lower()
                        else:
                            com = msg.strip()[1:].lower()
                        os.system(com)
                    else:
                        print(msg)
                except:
                    self.connected = False

    def inputHandler(self):
        while True:
            while self.connected:
                try:
                    msg=input().encode()
                    if(self.connected):
                        self.s.send(msg)
                except:
                    self.connected = False
    
    def connection(self):
        while True:
            while not self.connected:
                try:
                    self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    self.s.connect(('192.168.178.25',9090))
                    self.s.send(self.username.encode())
                    self.connected=True
                    os.system("cls")
                    if self.reconnect:
                        self.reconnect=False
                        print(bc().wColors['success']+'Connessione ristabilita!'+bc().reset)
                    break
                except:
                    self.reconnect=True
                    pass
                #time.sleep(1)
    
    def reconnectAnim(self):
        while True:
            while not self.connected:
                dots=''
                for i in range(4):
                    if not self.connected: # VEDERE QUI
                        os.system("cls")
                        print(bc().wColors['fail']+('Disconnesso, provando a riconnettermi'+dots)+bc().reset)
                        time.sleep(1)
                        dots+='.'
                    else:
                        break


if __name__ == "__main__":
    ansicon.load()
    os.system("cls")
    client = Client()
