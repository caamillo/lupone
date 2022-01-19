from Game.Util.player import Player
from Game.room import Room
from Game.Util.colors import bcolors as bc
import os
import socket
import threading
import random
import ansicon
import json
import pickle

class Server:
    def __init__(self,host=socket.gethostbyname(socket.gethostname()),port=9090):
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.players=[]
        self.rooms=[]
        self.colors=bc().sColors
        self.hallchat = False
        self.watchCommands = True
        self.startServer()

    def startServer(self):
        self.s.bind((self.host,self.port))
        self.s.listen(100)
        print(self.getStatus('Server {}:{} startato con successo'.format(str(self.host),str(self.port)),'success'))
        while True:
            c, addr = self.s.accept()
            username = c.recv(1024).decode()
            IsUsrInServ=True
            while IsUsrInServ:
                IsUsrInServ=False
                for i in self.players:
                    if i.username == username:
                        c.send(self.getStatus('Errore: questo utente è già connesso, inserire un altro username','fail').encode())
                        IsUsrInServ=True
                if IsUsrInServ:
                    username = c.recv(1024).decode()
            player=Player(len(self.players),c,username,self.getRandomColor())
            fa=self.findAccount(player)
            if fa>=0:
                c.send(self.getStatus('Questo account è già registrato, inserire la password per loggare','warning').encode())
                pw = c.recv(1024).decode()
                while(pw!=self.getAccount(fa)['password']):
                    c.send(self.getStatus('Errore: password non corretta.....','fail').encode())
                    pw = c.recv(1024).decode()
            c.send(self.getStatus('Connesso con successo','success').encode())
            self.broadcast(self.getStatus('{} se connesos'.format(username),'success'))
            self.players.append(player)
            threading.Thread(target=self.handleClient,args=(c,addr,)).start()
            threading.Thread(target=self.inputHandler,args=()).start()

    def broadcast(self,msg,c=None,text=False):
        if not text:
            print(msg)
            for connection in self.players:
                if not connection.isPlaying:
                    connection.client.send(msg.encode())
        else:
            p=self.getPlayerByClient(c)
            mm='{}: {}'.format(p.color+p.username,bc().reset+msg.decode())
            mm2='{}: {}'.format(p.color+'Tu',bc().reset+msg.decode())
            print(mm)
            for connection in self.players:
                if connection.client != c:
                    connection.client.send(mm.encode())
                else:
                    connection.client.send(mm2.encode())

    def broadcastRoom(self,msg,c,rid,text=False):
        if text:
            print(msg)
            for p in self.players:
                if p.isPlaying:
                    if p.room.id == rid:
                        p.client.send(msg.encode())
        else:
            pp=self.getPlayerByClient(c)
            mm='{}: {}'.format(pp.color+pp.username,bc().reset+msg.decode())
            mm2='{}: {}'.format(pp.color+'Tu',bc().reset+msg.decode())
            for p in self.players:
                if p.isPlaying:
                    if p.room.id == rid and p.client != c:
                        p.client.send(mm.encode())
                    elif p.room.id == rid and p.client == c:
                        p.client.send(mm2.encode())
    
    def handleClient(self,c,addr):
        while True:
            try:
                msg = c.recv(1024)
            except:
                if self.getPlayerByClient(c).isPlaying:
                    print(self.getStatus('{} è uscito da [{}#{}]'.format(self.getPlayerByClient(c).username,self.getPlayerByClient(c).room.name,self.getPlayerByClient(c).room.id),'fail'))
                    for i in self.getPlayerByClient(c).room.players:
                        if i.id!=self.getPlayerByClient(c).id:
                            i.client.send(self.getStatus('{} è uscito dalla stanza!'.format(self.getPlayerByClient(c).username),'fail').encode())
                    self.leaveRoom(self.getPlayerByClient(c).id)
                c.shutdown(socket.SHUT_RDWR)
                self.broadcast(self.getStatus('{} se dato'.format(self.removePlayerByClient(c).username),'fail'))
                break
            if str(msg.decode()).strip() != '' and str(msg.decode()).strip()[0]!='/':
                if self.hallchat:
                    self.broadcast(msg,c,True)
                elif self.getPlayerByClient(c).isPlaying:
                    self.broadcastRoom(msg,c,self.getPlayerByClient(c).room.id)
            elif(str(msg.decode()).strip()[0]=='/'):
                self.getCommand(msg.decode().strip(),c)
    
    def inputHandler(self):
        while True:
            self.getCommand(input(),None,console=True)

    def getCommand(self,msg,c,console=False):
        if len(msg) > 1:
            args=msg.split()[1:]
            if len(args)>0:
                com = msg[1:msg.find(' ')].lower()
            else:
                com = msg[1:].lower()
            #print(com)
            if com == 'createroom' and self.limComm(args,2,c,console):
                room = self.createRoom(args[0],args[1])
                if self.watchCommands:
                    print(self.getStatus('{} ha creato la stanza [{}#{}]'.format(self.getPlayerByClient(c).username,room.name,room.id),'success'))
                self.pCOC(self.getStatus('Stanza [{}#{}] creata con succesos'.format(room.name,room.id),'success'),c,console)
            elif com == 'removeroom' and self.limComm(args,1,c,console):
                room = self.removeRoom(args[0])
                if self.watchCommands:
                    print(self.getStatus('{} ha rimosso la stanza [{}#{}]'.format(self.getPlayerByClient(c).username,room.name,room.id),'success'))
                self.pCOC(self.getStatus('Stanza [{}#{}] rimossa con succesos'.format(room.name,room.id),'success'),c,console)
            elif com == 'listrooms':
                self.pCOC(self.getStatus('Stanze Aperte:','okblue'),c,console)
                for i in self.rooms:
                    self.pCOC(self.getStatus('Stanza [{}#{}]\n'.format(i.name,i.id),'okblue'),c,console)
            elif com == 'cls':
                self.pCOC('/cls',c,console)
            elif not console:
                if com == 'join' and self.limComm(args,1,c,console):
                    if(self.joinRoom(int(self.getPlayerByClient(c).id),int(args[0]))):
                        if self.watchCommands:
                            print(self.getStatus('{} è entrato in [{}#{}]'.format(self.getPlayerByClient(c).username,self.rooms[int(args[0])].name,self.rooms[int(args[0])].id),'success'))
                        self.pCOC(self.getStatus('Sei entrato in [{}#{}]'.format(self.rooms[int(args[0])].name,self.rooms[int(args[0])].id),'success'),c,console)
                        for i in self.rooms[int(args[0])].players:
                            if i.id!=self.getPlayerByClient(c).id:
                                i.client.send(self.getStatus('{} è entrato in stanza!'.format(self.getPlayerByClient(c).username),'success').encode())
                    else:
                        self.pCOC(self.getStatus('Errore: impossibile unirsi in stanza!','fail'),c,console)
                elif com == 'leave':
                    room=self.getPlayerByClient(c).room
                    if(self.leaveRoom(int(self.getPlayerByClient(c).id))):
                        if self.watchCommands:
                            print(self.getStatus('{} è uscito da [{}#{}]'.format(self.getPlayerByClient(c).username,room.name,room.id),'fail'))
                        self.pCOC(self.getStatus('Sei uscito da [{}#{}]'.format(room.name,room.id),'success'),c,console)
                        for i in self.rooms[room.id].players:
                            if i.id!=self.getPlayerByClient(c).id:
                                i.client.send(self.getStatus('{} è uscito dalla stanza!'.format(self.getPlayerByClient(c).username),'fail').encode())
                    else:
                        self.pCOC(self.getStatus('Errore: impossibile uscire dalla stanza!','fail'),c,console)
                elif com == 'setpassword' and self.limComm(args,1,c,console):
                    if(self.addAccount(self.getPlayerByClient(c),args[0])):
                        self.pCOC(self.getStatus('Account aggiunto con successo','success'),c,console)
                    else:
                        self.pCOC(self.getStatus('Impossibile aggiungere il profilo','fail'),c,console)
            elif console:
                if com == 'watchcom' and self.limComm(args,1,c,console):
                    if args[0].lower() == 'true':
                        print(self.getStatus('Toggle WatchCom','success'))
                        self.watchCommands = True
                    else:
                        print(self.getStatus('Toggle WatchCom','fail'))
                        self.watchCommands = False
                elif com == 'isgame' and self.limComm(args,1,c,console):
                    if(len(self.rooms)>int(args[0]) and int(args[0])>=0):
                        print(self.getStatus(self.rooms[int(args)]).isGame(),'warning')
                    else:
                        print(self.getStatus('Room not found','fail'))
                elif com == 'admin' and self.limComm(args,1,c,console):
                    playerFound=self.findPlayer(int(args[0]))
                    if playerFound>=0:
                        if not self.players[playerFound].admin:
                            self.players[playerFound].admin=True
                            if not self.isAdmin(self.players[playerFound].username):
                                with open('admins.pkl','wb') as f:
                                    pickle.dump(self.players[playerFound].username,f)
                        else:
                            print(self.getStatus('Questo utente è già admin','warning'))
            else:
                self.pCOC(self.getStatus('Comando inesistente','fail'),c,console)
        else:
            self.pCOC(self.getStatus('Comando inesistente','fail'),c,console)

    def pCOC(self,text,c,console=False):
        if not console:
            c.send(text.encode())
        else:
            if(text.strip()[0]=='/'):
                args=text.strip().split()[1:]
                if len(args)>0:
                    com = text.strip()[1:text.strip().find(' ')].lower()
                else:
                    com = text.strip()[1:].lower()
                os.system(com)
            else:
                print(text)

    def limComm(self,args,lenargs,c,console=False):
        if(len(args)==lenargs):
            return True
        elif(len(args)<lenargs):
            self.pCOC(self.getStatus('Errore: inserire più argomenti','fail'),c,console)
        elif(len(args)>lenargs):
            self.pCOC(self.getStatus('Errore: inserire meno argomenti','fail'),c,console)
        return False

    def addAccount(self,p,pw):
        if self.findAccount(p)<0:
            for i in self.players:
                if p.id == i.id:
                    if os.path.getsize('profiles.json')>0:
                        with open('profiles.json','r',encoding='utf-8') as f:
                            data=json.load(f)
                    else:
                        data=dict()
                    with open('profiles.json','w',encoding='utf-8') as f:
                        pp={
                            'username':p.username,
                            'color':bc().getStrColorByAnsi(p.color),
                            'admin':p.admin,
                            'password':pw
                        }
                        self.players[p.id].setPassword(pw)
                        data[p.username]=pp
                        json.dump(data,f)
                    return True
        return False
    
    def removeAccount(self,p):
        if os.path.getsize('profiles.json')>0:
            if self.findAccount(p) > 0:
                with open('profiles.json','r',encoding='utf-8') as f:
                    data=json.load(f)
                with open('profiles.json','w',encoding='utf-8') as f:
                    for i in data:
                        if i==p.username:
                            del data[i]
                    json.dump(data,f)
                return True
        return False

    def getAccount(self,n):
        if os.path.getsize('profiles.json')>0:
            with open('profiles.json','r',encoding='utf-8') as f:
                data=json.load(f)
            for c,i in enumerate(data):
                if c == n:
                    return data[i]
        return None

    def findAccount(self,p):
        if os.path.getsize('profiles.json')>0:
            with open('profiles.json','r',encoding='utf-8') as f:
                data=json.load(f)
            for c,i in enumerate(data):
                if i==p.username:
                    return c
        return -1

    def createRoom(self,name,type):
        if type.lower() == 'normal':
            room = Room(len(self.rooms),name)
            self.rooms.append(room)
            return room
        elif type.lower() == 'lupone':
            room = Room(len(self.rooms),name,game=True,server=self)
            self.rooms.append(room)
            return room
    
    def removeRoom(self,id):
        for i in self.rooms:
            if i.id == id:
                room=i
                for j in self.players:
                    self.leaveRoom(j.id,j,room.id)
                self.rooms.remove(i)
                return room
        return False

    def joinRoom(self,pid,rid):
        if not self.players[pid].isPlaying and ((self.rooms[rid].maxPlayers>=len(self.rooms[rid].players)) or self.rooms[rid].maxPlayers<0):
            if(self.rooms[rid].game):
                if(self.rooms[rid].gameroom.gameStarted):
                    return False
            v=self.rooms[rid].addPlayer(self.players[pid])
            if v:
                self.players[pid].isPlaying=True
                self.players[pid].room=self.rooms[rid]
                return True
        return False

    def leaveRoom(self,pid):
        if self.players[pid].isPlaying:
            self.rooms[self.players[pid].room.id].removePlayer(pid)
            self.players[pid].isPlaying = False
            self.players[pid].room = None
            return True
        return False

    def getStatus(self,text,status):
        return bc().getWColors()[status]+text+bc().reset

    def getRandomColor(self):
        indColor = random.randrange(0,len(self.colors))
        color = self.colors[indColor]
        del self.colors[indColor]
        return color

    def findPlayer(self,ind):
        for c,i in enumerate(self.players):
            if i.id == ind:
                return c
        else:
            return -1


    def getPlayerByClient(self,c):
        for i in self.players:
            if c == i.client:
                return i
        return False

    def removePlayerByClient(self,c):
        for i in self.players:
            if c == i.client:
                p=i
                self.players.remove(i)
                return p
        return False

    def isAdmin(self,nick):
        if os.path.getsize('admins.pkl')>0:
            with open('admins.pkl','rb') as f:
                try:
                    admins=pickle.load(f) # continuare
                    for i in admins:
                        if i == nick:
                            return True
                except:
                    return False
        return False

if __name__ == "__main__":
    ansicon.load()
    os.system("cls")
    server = Server()
