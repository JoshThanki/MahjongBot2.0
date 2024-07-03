import json
import random
import numpy as np
from numpy.typing import NDArray
from Global import *


from matrix import Matrix

 #Creates a dictionary containing an entire set of tiles

class Game():
    
    def __init__(self):

        self.gameData = GameData()
        self.gameData.initGame()

        
    
        
    
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


class GameData(Matrix):
    with open('tiles.json', 'r') as file:
        start_tiles = json.load(file)

    def __init__(self):

        self._tileWall = GameData.start_tiles

        #self.orderedMelds = [[[5,6,7] , [5,5,5], [] ],[],[],[]]
        self.orderedMelds = [[],[],[],[]]

        #self.orderedPool = [[1,2,4,6],[],[],[]]
        self.orderedPool = [[],[],[],[]]

        super().__init__()

    
    def initGame(self):
        ()
    
    






gameData = GameData()

print(gameData.wallTiles)
