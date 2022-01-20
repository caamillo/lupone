from ast import arg
from Game.Util.player import Player
from Game.room import Room
from Game.Util.colors import bcolors as bc
import os
import socket
import threading
import random
import ansicon
import json
# Day 13
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
        self.yes = ['yes','si','y','s','true','t']
        self.no = ['no','n','false','f']
        self.startServer()

    def startServer(self):
        self.s.bind((self.host,self.port))
        self.s.listen(100)
        print(self.getStatus('Server {}:{} startato con successo'.format(str(self.host),str(self.port)),'success'))
        threading.Thread(target=self.inputHandler,args=()).start()
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
            player=Player(len(self.players),c,username)
            fa=self.findAccount(player)
            if fa>=0:
                try:
                    c.send(self.getStatus('Questo account è già registrato, inserire la password per loggare','warning').encode())
                    pw = c.recv(1024).decode()
                    while(pw!=self.getAccount(fa)['password']):
                        c.send(self.getStatus('Errore: password non corretta.....','fail').encode()) # FIX
                        pw = c.recv(1024).decode()
                    color = self.pickColor(bc().getAnsiByStrColor(self.getAccount(fa)['chatColor']))
                    player.setColor(color)
                    c.send(self.getStatus('Connesso con successo','success').encode())
                    self.broadcast(self.getStatus('{} se connesos'.format(username),'success'))
                    self.players.append(player)
                    threading.Thread(target=self.handleClient,args=(c,addr,)).start()
                except:
                    c.close()
            else:
                color = self.getRandomColor()
                player.setColor(color)
                c.send(self.getStatus('Connesso con successo','success').encode())
                self.broadcast(self.getStatus('{} se connesos'.format(username),'success'))
                self.players.append(player)
                threading.Thread(target=self.handleClient,args=(c,addr,)).start()

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
                comExec=self.getCommand(msg.decode().strip(),c)
                if comExec == None:
                    self.pCOC(self.getStatus('Comando inesistente','fail'),c)
    
    def inputHandler(self):
        while True:
            comExec=self.getCommand(input(),None,console=True)
            if comExec == None:
                print(self.getStatus('Comando inesistente','fail'))

    def getCommand(self,msg,c,console=False):
        if len(msg) > 1:
            args=msg.split()[1:]
            if len(args)>0:
                com = msg[1:msg.find(' ')].lower()
            else:
                com = msg[1:].lower()
            #print(com)
            if com == 'listrooms': # vedere se funziona
                self.pCOC(self.getStatus('Stanze Aperte:','okblue'),c,console)
                for i in self.rooms:
                    self.pCOC(self.getStatus('Stanza [{}#{}]\n'.format(i.name,i.id),'okblue'),c,console)
                return True
            elif com == 'cls':
                self.pCOC('/cls',c,console)
            if self.isAdmin(self.getPlayerByClient(c)):
                if com == 'createroom' and self.limComm(args,1,c,console,unlimited=True):
                    room = None
                    if len(args)>1:
                        room = self.createRoom(args[0],args[1])
                    else:
                        room = self.createRoom(args[0],'default')
                    if room != None:
                        if self.watchCommands:
                            print(self.getStatus('{} ha creato la stanza [{}#{}]'.format(self.getPlayerByClient(c).username,room.name,room.id),'success'))
                        self.pCOC(self.getStatus('Stanza [{}#{}] creata con succesos'.format(room.name,room.id),'success'),c,console)
                        return True
                    self.pCOC(self.getStatus('Impossibile creare la stanza','fail'),c,console)
                    return False
                elif com == 'removeroom' and self.limComm(args,1,c,console):
                    room = None
                    room = self.removeRoom(args[0])
                    if(room!=None):
                        if self.watchCommands:
                            print(self.getStatus('{} ha rimosso la stanza [{}#{}]'.format(self.getPlayerByClient(c).username,room.name,room.id),'success'))
                        self.pCOC(self.getStatus('Stanza [{}#{}] rimossa con succesos'.format(room.name,room.id),'success'),c,console)
                        return True
                    self.pCOC(self.getStatus('Impossibile rimuovere la stanza','fail'),c,console)
                    return False
                elif com == 'kick' and self.limComm(args,1,c,console):
                    playerFound = self.players[self.findPlayer(args[0])]
                    if playerFound != None: # Fix
                        if self.kickPlayer(playerFound):
                            self.pCOC(self.getStatus('{} kickato'.format(playerFound.username),'fail'),c,console)
                        else:
                            self.pCOC(self.getStatus('Impossibile kickare il player','fail'),c,console)
                    else:
                        self.pCOC(self.getStatus('Player non trovato','fail'),c,console)
                    return False
            elif not console:
                if com == 'join' and self.limComm(args,1,c,console):
                    if(self.joinRoom(int(self.getPlayerByClient(c).id),int(args[0]))):
                        if self.watchCommands:
                            print(self.getStatus('{} è entrato in [{}#{}]'.format(self.getPlayerByClient(c).username,self.rooms[int(args[0])].name,self.rooms[int(args[0])].id),'success'))
                        self.pCOC(self.getStatus('Sei entrato in [{}#{}]'.format(self.rooms[int(args[0])].name,self.rooms[int(args[0])].id),'success'),c,console)
                        for i in self.rooms[int(args[0])].players:
                            if i.id!=self.getPlayerByClient(c).id:
                                i.client.send(self.getStatus('{} è entrato in stanza!'.format(self.getPlayerByClient(c).username),'success').encode())
                        return True
                    else:
                        self.pCOC(self.getStatus('Errore: impossibile unirsi in stanza!','fail'),c,console)
                    return False
                elif com == 'leave':
                    room=self.getPlayerByClient(c).room
                    if(self.leaveRoom(int(self.getPlayerByClient(c).id))):
                        if self.watchCommands:
                            print(self.getStatus('{} è uscito da [{}#{}]'.format(self.getPlayerByClient(c).username,room.name,room.id),'fail'))
                        self.pCOC(self.getStatus('Sei uscito da [{}#{}]'.format(room.name,room.id),'success'),c,console)
                        for i in self.rooms[room.id].players:
                            if i.id!=self.getPlayerByClient(c).id:
                                i.client.send(self.getStatus('{} è uscito dalla stanza!'.format(self.getPlayerByClient(c).username),'fail').encode())
                        return True
                    else:
                        self.pCOC(self.getStatus('Errore: impossibile uscire dalla stanza!','fail'),c,console)
                    return False
                elif com == 'setpassword' and self.limComm(args,1,c,console):
                    if(self.addAccount(self.getPlayerByClient(c),args[0])):
                        self.pCOC(self.getStatus('Account aggiunto con successo','success'),c,console)
                        return True
                    else:
                        self.pCOC(self.getStatus('Impossibile aggiungere il profilo','fail'),c,console)
                    return False
                elif com == 'changepassword' and self.limComm(args,1,c,console):
                    if os.path.getsize('profiles.json')>0:
                        if(self.changePassword(self.getPlayerByClient(c),args[0])):
                            self.pCOC(self.getStatus('Password cambiata con successo','success'),c,console)
                            return True
                        else:
                            self.pCOC(self.getStatus('Account non trovato','fail'),c,console)
                    else:
                        self.pCOC(self.getStatus('Account non trovato','fail'),c,console)
                    return False
                elif com in ['privmsg','privatemsg','privatemessage'] and self.limComm(args,2,c,console):
                    playerFound=self.getPlayerByUsername(args[0])
                    if playerFound!=None:
                        if len(args[1].strip())>0:
                            if(self.privateMessage(self.getPlayerByClient(c),playerFound,args[1].strip())):
                                self.pCOC(self.getStatus('Messaggio inviato con successo','success'),c,console)
                                return True
                            else:
                                self.pCOC(self.getStatus('Errore: Messaggio non inviato','fail'),c,console)
                        else:
                            self.pCOC(self.getStatus('Impossibile inviare un messaggio vuoto','fail'),c,console)
                    else:
                        self.pCOC(self.getStatus('Player not found','fail'),c,console)
                    return False
            elif console:
                if com == 'watchcom' and self.limComm(args,1,c,console):
                    toggle = self.isYesOrNo(args[0])
                    if toggle != None:
                        self.watchCommands = toggle
                        if toggle:
                            print(self.getStatus('Toggle WatchCom','success'))
                        else:
                            print(self.getStatus('Toggle WatchCom','fail'))
                        return True
                    return False
                elif com == 'isgame' and self.limComm(args,1,c,console):
                    if(len(self.rooms)>int(args[0]) and int(args[0])>=0):
                        print(self.getStatus(self.rooms[int(args)]).isGame(),'warning')
                        return True
                    else:
                        print(self.getStatus('Room not found','fail'))
                    return False
                elif com == 'admin' and self.limComm(args,2,c,console):
                    toggle=self.isYesOrNo(args[1])
                    if toggle != None:
                        playerFound=self.findPlayer(int(args[0]))
                        if playerFound>=0 and os.path.getsize('profiles.json')>0 and self.findAccount(self.players[playerFound])>=0:
                            with open('profiles.json','r') as f:
                                data=json.load(f)
                            with open('profiles.json','w') as f:
                                self.players[playerFound].admin=toggle
                                data[self.players[playerFound].username]['isAdmin']=toggle
                                json.dump(data,f)
                                if toggle:
                                    print(self.getStatus('{} è diventato admin'.format(self.players[playerFound].username),'success'))
                                    self.players[playerFound].client.send(self.getStatus('Hai i privilegi di amministratore','success').encode())
                                else:
                                    print(self.getStatus('{} non è più admin'.format(self.players[playerFound].username),'fail'))
                                    self.players[playerFound].client.send(self.getStatus('Non hai più i privilegi di amministratore','fail').encode())
                            return True
                        else:
                            print(self.getStatus('Account non trovato','fail'))
                    else:
                        print(self.getStatus('Inserire True o False','fail'))
                    return False
        return None

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
    
    def privateMessage(self,fromm,to,msg):
        for i in self.players:
            if i.id == to.id:
                i.client.send((self.getStatus('Private msg from {}: '.format(fromm.username),'okcyan')+msg).encode())
                return True
        return False

    def limComm(self,args,lenargs,c,console=False,unlimited=False):
        if(len(args)==lenargs):
            return True
        elif(len(args)<lenargs):
            self.pCOC(self.getStatus('Errore: inserire più argomenti','fail'),c,console)
        elif(len(args)>lenargs):
            if unlimited:
                return True
            else:
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
                            'chatColor':bc().getStrColorByAnsi(p.color),
                            'isAdmin':p.admin,
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

    def changePassword(self,p,pw):
        fa=self.findAccount(p)
        with open('profiles.json','r',encoding='utf-8') as f:
            data=json.load(f)
        with open('profiles.json','w',encoding='utf-8') as f:
            for c,i in enumerate(data):
                if fa == c:
                    data[i]['password']=pw
            json.dump(data,f)
            return True
        return False

    def createRoom(self,name,type):
        if type.lower() == 'default':
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
        return None

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

    def kickPlayer(self,p):
        for i in self.players:
            if p.id == i.id:
                i.client.close()
                return True
        return False

    def pickColor(self,color):
        for c,i in enumerate(self.colors):
            if i == color:
                ansiColor = self.colors[c]
                del self.colors[c]
                return ansiColor
        return None

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

    def getPlayerByUsername(self,usr):
        for i in self.players:
            if i.username == usr:
                return i
        return None

    def isAdmin(self,player):
        if os.path.getsize('profiles.json')>0:
            with open('profiles.json','r') as f:
                try:
                    profiles=json.load(f)
                    for i in profiles:
                        if i == player.username:
                            return profiles[i]['isAdmin']
                except:
                    return False
        return False

    def isYesOrNo(self,s):
        if s.lower() in self.yes:
            return True
        if s.lower() in self.no:
            return False
        return None

if __name__ == "__main__":
    ansicon.load()
    os.system("cls")
    server = Server()
