import json
import random
import numpy as np


with open('tiles.json', 'r') as file:
    start_tiles = json.load(file) #Creates a dictionary containing an entire set of tiles

class Game:
    def __init__(self):

        self.gameState = np.zeros((11, 34))

        self.windDict = {
            "e_wind": 0,
            "s_wind": 1,
            "w_wind": 2,
            "n_wind": 3,
        }

    def setRoundWind(self, wind):
        windNum = self.windDict[wind]
        self.gameState[0][0] = windNum

    def getRoundWind(self):
        reversedWindDict = {v: k for k, v in self.windDict.items()}
        return reversedWindDict[self.gameState[0][0]]
    

    def setDealer(self, dealer):
        self.gameState[0][1] = dealer
    
    def getDealer(self):
        return self.gameState[0][1]

    def setHonbaSticks(self, amount):
        self.gameState[0][3] = amount
    
    def getHonbaSticks(self):
        return self.gameState[0][3]
    
    def setRiichiSticks(self, amount):
        self.gameState[0][4] = amount
    
    def getRiichiSticks(self):
        return self.gameState[0][4]
    
    def setWallTiles(self, amount):
        self.gameState[0][5] = amount
    
    def decWallTiles(self):
        self.gameState[0][5] -=1

    def getWallTiles(self):
        return self.gameState[0][5]
    
    def setPlayerScore(self, player, score):
        if player in [0,1,2,3]:
            self.gameState[0][6+player] = score
        else:
            print("Invalid Player")
    
    def getPlayerScore(self, player):
        if player in [0,1,2,3]:
            return self.gameState[0][6+player]
        else:
            print("Invalid Player")

    def setPlayerRiichi(self, player):
        if player in [0,1,2,3]:
            self.gameState[0][10+player] = 1
        else:
            print("Invalid Player")
    
    def getPlayerRiichiStat(self, player):
        if player in [0,1,2,3]:
            return self.gameState[0][10+player]
        else:
            print("Invalid Player")
    


