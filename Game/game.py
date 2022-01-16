from Game.Util.ruoli import Ruoli
import random as rnd

class Game:
    def __init__(self,gameroom):
        self.ruoli=Ruoli()
        self.gm=gameroom
        self.players=self.gm.players
        self.s=self.gm.s
        self.gameRuoli=self.loadGameRuoli()
    
    def loadGameRuoli(self):
        goodRuoli = self.ruoli.getRuoliByType('good')
        badRuoli = self.ruoli.getRuoliByType('bad')
        neutralRuoli = self.ruoli.getRuoliByType('neutral')
        
        gameRuoli = list()
        for i in range(4):
            ruolo = rnd.choice(goodRuoli)
            gameRuoli.append(ruolo)
            goodRuoli.remove(ruolo)
        for i in range(3):
            ruolo = rnd.choice(badRuoli)
            gameRuoli.append(ruolo)
            badRuoli.remove(ruolo)
        for i in range(2):
            ruolo = rnd.choice(neutralRuoli)
            gameRuoli.append(ruolo)
            neutralRuoli.remove(ruolo)
        
        return gameRuoli
    
    def loopGame(self):
        self.s.broadcastRoom(self.s.getStatus('Gioco iniziato!','success'),None,self.gm.id,True)
