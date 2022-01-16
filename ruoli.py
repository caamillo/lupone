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