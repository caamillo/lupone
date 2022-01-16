from gameroom import GameRoom
class Room:
    def __init__(self,id,name,game=False,server=None,max=-1): #boolean gameroom = true
        self.id=id
        self.name=name
        self.players=[]
        self.maxPlayers=max
        self.game=game
        self.server=server
        if self.game:
            if max>=0:
                self.gameroom=GameRoom(self,max=max)
            else:
                self.gameroom=GameRoom(self)
    def addPlayer(self,player):
        if self.game:
            return self.gameroom.onJoin(player)
        self.players.append(player)
        return True
    def playerExsists(self,id):
        for i in self.players:
            if i.id == id:
                return True
        return False
    def removePlayer(self,id):
        for i in self.players:
            if i.id == id:
                self.players.remove(i)
                return True
        return False
    def isGame(self):
        return self.game
