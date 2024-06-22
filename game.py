import json
import random
import numpy as np
from numpy.typing import NDArray


 #Creates a dictionary containing an entire set of tiles

class Game:
    with open('tiles.json', 'r') as file:
        start_tiles = json.load(file)

    windDict = {
        "e_wind": 0,
        "s_wind": 1,
        "w_wind": 2,
        "n_wind": 3,
    }

    strToIndex = {
        "1_char": 0,
        "2_char": 1,
        "3_char": 2,
        "4_char": 3,
        "5_char": 4,
        "6_char": 5,
        "7_char": 6,
        "8_char": 7,
        "9_char": 8,
        "1_circ": 9,
        "2_circ": 10,
        "3_circ": 11,
        "4_circ": 12,
        "5_circ": 13,
        "6_circ": 14,
        "7_circ": 15,
        "8_circ": 16,
        "9_circ": 17,
        "1_bamb": 18,
        "2_bamb": 19,
        "3_bamb": 20,
        "4_bamb": 21,
        "5_bamb": 22,
        "6_bamb": 23,
        "7_bamb": 24,
        "8_bamb": 25,
        "9_bamb": 26,
        "e_wind": 27,
        "s_wind": 28,
        "w_wind": 29,
        "n_wind": 30,
        "w_drag": 31,
        "g_drag": 32,
        "r_drag": 33
    }

    indexToStr = {v: k for k, v in strToIndex.items()}

    def __init__(self):

        self.gameState = np.zeros((11, 34))
        self._tileWall = Game.start_tiles
    
    #gamestate conversion functions:

    def setRoundWind(self, wind):
        windNum = Game.windDict[wind]
        self.gameState[0][0] = windNum

    def getRoundWind(self):
        reversedWindDict = {v: k for k, v in Game.windDict.items()}
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
    
    def addDoraIndicator(self, doraIndicator: str):
        self.gameState[1][self.strToIndex[doraIndicator]] += 1
    
    def getDoraIndicators(self):
        return self.vectorToReadable(self.gameState[1])
    
    @staticmethod
    def readableToVector(readableHand: list):
        vectorHand = np.zeros(34)
        for i in readableHand:
            vectorHand[Game.strToIndex[i]] += 1
        return vectorHand
    
    @staticmethod
    def vectorToReadable(vectorHand: NDArray):
        readableHand = []
        for i in range(34):
            for j in range(int(vectorHand[i])):
                readableHand.append(Game.indexToStr[i])
        return readableHand
    
    #game action functions:

    def draw(self):
        availableTile = list(self._tileWall.keys())
        numAvailable = list(self._tileWall.values())

        drawnTile = random.choices(availableTile, weights=numAvailable, k=1)[0]
        self._tileWall[drawnTile] -= 1
        return drawnTile
    
if False: #add tests here
    testGame = Game()

    testGame.gameState[1][1] = 1
    testGame.addDoraIndicator("3_char")
    testGame.addDoraIndicator("3_char")
    doraIndicators = testGame.getDoraIndicators()
    print(doraIndicators)

    doraIndicatorsVectors = testGame.readableToVector(doraIndicators)
    print(doraIndicatorsVectors)

    print(testGame.draw())
    print(testGame._tileWall)