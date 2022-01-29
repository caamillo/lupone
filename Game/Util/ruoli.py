import json
class Ruoli:
    def __init__(self):
        self.ruoli=dict()
        self.loadRuoli()
    def loadRuoli(self):
        with open('ruoli.json','r') as f:
            self.ruoli=json.loads(f.read())
    def getAllRuoli(self):
        return self.ruoli
    def getRuoliByType(self,type):
        ruoli = list()
        for i in self.ruoli:
            for j in self.ruoli[i]:
                if str(self.ruoli[i][j]).lower() == type.lower():
                    ruoli.append(self.ruoli[i])
        return ruoli
    def getRuoloIdByName(self,name): # self.getRuoloIdByName('bodyguard')
        for i in self.ruoli:
            for j in self.ruoli[i]:
                if name.lower() == str(self.ruoli[i][j]).lower():
                    return self.ruoli[i]['id']
class Cittadini:
    def __init__(self,player=None):
        self.player=player
        self.players=[]
    def addPlayer(self,player):
        self.players.append(player)
    def getJson(self):
        return {
            "id":-1,
            "name":"Cittadino",
            "type":"good"
        }
class Lupi:
    def __init__(self,player=None):
        self.player=player
        self.players=[]
    def addPlayer(self,player):
        self.players.append(player)
    def getJson(self):
        return Ruoli().getAllRuoli()['lupo']
class Capobranco:
    def __init__(self,player=None):
        self.player=player
    def getJson(self):
        return Ruoli().getAllRuoli()['capobranco']
class Bodyguard:
    def __init__(self,player=None):
        self.player=player
    def getJson(self):
        return Ruoli().getAllRuoli()['bodyguard']
class Jailor:
    def __init__(self,player=None):
        self.player=player
    def getJson(self):
        return Ruoli().getAllRuoli()['jailor']
class Investigatore:
    def __init__(self,player=None):
        self.player=player
    def getJson(self):
        return Ruoli().getAllRuoli()['investigatore']
class Medium:
    def __init__(self,player=None):
        self.player=player
    def getJson(self):
        return Ruoli().getAllRuoli()['medium']
class Jester:
    def __init__(self,player=None):
        self.player=player
    def getJson(self):
        return Ruoli().getAllRuoli()['jester']
class Esecutore:
    def __init__(self,player=None):
        self.player=player
    def getJson(self):
        return Ruoli().getAllRuoli()['esecutore']
class Sciamano:
    def __init__(self,player=None):
        self.player=player
    def getJson(self):
        return Ruoli().getAllRuoli()['sciamano']
