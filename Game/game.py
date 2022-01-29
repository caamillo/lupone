from sqlalchemy import join
from Game.Util.ruoli import Cittadini,Lupi,Capobranco,Bodyguard,Jailor,Investigatore,Medium,Jester,Esecutore,Sciamano
from Game.Util.ruoli import Ruoli
from threading import Thread
import random as rnd
import time

class Game:
    def __init__(self,gameroom):
        self.ruoli=Ruoli()
        self.gm=gameroom
        self.players=self.gm.players
        self.s=self.gm.s
        self.gameRuoli=None
        self.endGame=False
        # introdurre i cittadini, fare metodo per aggiungerli
        # ogni 4 un lupo, minimo 6 giocatori e si parte da 2 lupi
    
    def loadGameRuoli(self):
        objRuoli=[Cittadini(),Lupi(),Capobranco(),Bodyguard(),Jailor(),Investigatore(),Medium(),Jester(),Esecutore(),Sciamano()]
        selPlayers=self.players
        gameRuoli=list()
        nRuoli={
            "Cittadino":2,
            "Lupo":1,
            "Capobranco":1,
            "Bodyguard":1,
            "Jailor":0,
            "Investigatore":1,
            "Medium":0,
            "Jester":0,
            "Esecutore":0,
            "Sciamano":0
        }
        for i in range(6,len(self.players)):
            if i == 6:
                nRuoli['Jester']+=1
            elif i == 7:
                nRuoli['Cittadino']+=1
            elif i == 8:
                nRuoli['Jailor']+=1
            elif i == 9:
                nRuoli['Lupo']+=1
            elif i == 10:
                nRuoli['Esecutore']+=1
            elif i == 11:
                nRuoli['Cittadino']+=1
            elif i == 12:
                nRuoli['Medium']+=1
            elif i == 13:
                nRuoli['Sciamano']+=1
        for i in nRuoli:
            if nRuoli[i]>0:
                if nRuoli[i]<2:
                    for j in objRuoli:
                        if j.getJson()['name']==i:
                            rndPlayer=rnd.choice(selPlayers)
                            j.__init__(rndPlayer)
                            gameRuoli.append(j)
                            selPlayers.remove(rndPlayer)
                            break
                else:
                    for j in objRuoli:
                        if j.getJson()['name']==i:
                            gameRuoli.append(j)
                            for i in range(nRuoli[i]):
                                rndPlayer=rnd.choice(selPlayers)
                                gameRuoli[-1].addPlayer(rndPlayer)
                                selPlayers.remove(rndPlayer)
                            break
        return gameRuoli
    
    def loopGame(self):
        self.s.broadcastRoom(self.s.getStatus('Gioco iniziato!','success'),None,self.gm.id,True)
        self.gameRuoli=self.loadGameRuoli()
        for i in self.gameRuoli:
            if i.player!=None:
                print(i.getJson()['name'],i.player.username)
            else:
                for j in i.players:
                    print(i.getJson()['name'],j.username)
        while not self.endGame:
            pass
