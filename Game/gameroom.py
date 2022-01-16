from Game.game import Game
from threading import Thread
from Game.Util.colors import bcolors as bc
import os
import time
import socket

class GameRoom():
    def __init__(self,room,min=1,max=2):
        self.room = room
        self.id=room.id
        self.name=room.name
        self.players=room.players
        self.s=room.server
        self.gameStarted = False
        self.minPlayers=min
        self.maxPlayers=max
        self.game = Game(self)
        self.playerjoined=False
        waitplayersjointhread=Thread(target=self.waitPlayersJoin,args=())
        waitplayersjointhread.start()
    def waitPlayersJoin(self):
        while True:
            while not self.gameStarted:
                time.sleep(1)
                if self.playerjoined:
                    self.playerjoined=False
                    self.comEveryone('cls')
                    if len(self.players)<self.minPlayers:
                        self.s.broadcastRoom(self.s.getStatus('Stanza in attesa, mancano {} giocatori ({}/{})'.format(self.minPlayers-len(self.players),len(self.players),self.minPlayers),'warning'),None,self.id,True)
                    else:
                        self.gameStarted=True
                        self.startGame()
    def cooldown(self,t,text):
        for i in reversed(range(1,t)):
            self.s.broadcastRoom('{} {}'.format(text,str(i)),None,self.id,True)
            time.sleep(1)
    def startGame(self):
        self.cooldown(5,'Il Gioco inizia tra..')
        self.game.loopGame()
    def comEveryone(self,com):
        for i in self.players:
            i.client.send(f'/{com}'.encode())
    def onJoin(self,player):
        if self.maxPlayers>=len(self.players)+1:
            self.players.append(player)
            self.playerjoined = True
            return True
        return False

    
