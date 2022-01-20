class Player:
    def __init__(self,id,client,username):
        self.id=id
        self.client=client
        self.username=username
        self.color=None
        self.isPlaying=False
        self.room=None
        self.admin=False
        self.password=None
    def setPassword(self,pw):
        self.password=pw
    def setColor(self,c):
        self.color=c
