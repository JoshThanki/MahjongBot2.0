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
    
    #points [1,2,3,4], dealer (0-3), roundWind (0-3) honbaSticks (int)

    def __init__(self, points = [250,250,250,250], dealer = 0, roundWind = 0, honbaSticks = 0):
        
        ### Define Variables ###

        with open('tiles.json', 'r') as file:
            self.start_tiles = json.load(file)

        #self.orderedMelds = [[([5,6,7],1) , ([5,5,5],1) , [] ],[],[],[]]
        self.orderedMelds = [[],[],[],[]]

        #self.orderedPool = [[1,2,4,6],[],[],[]]
        self.orderedPool = [[],[],[],[]]

        self.orderedDora = []

        super().__init__()

        ### Initialise Game ###

        self.tilePool = self.start_tiles
            
        initialHands = [[self.getRandTile() for i in range(13)] for j in range(4)]
        
        #sets points
        self.setPlayerScore(points)
        
        #sets player winds
        self.setDealer(dealer)
        self.setPlayerWinds()

        #sets starting hands
        self.initialisePrivateHands(initialHands)

        #sets more metadata form seed
        
        self.setHonbaSticks(honbaSticks)
        self.setRoundWind(roundWind)

    

    def getRandTile(self):
        keys, weights = zip(*self.tilePool.items())

        if any(weights):
            self.tempRandomElement = random.choices(keys, weights=weights)[0]
            self.tilePool[self.tempRandomElement] -= 1
            return self.tempRandomElement
        
        else:
            return None

    def getNumKans(self):
        sum(self.kansNum)

    def newDora(self):
        dora = self.getRandTile()
        self.addDoraIndicator(dora)


    ### Overriden Methods ### 

    def addPlayerPool(self, player, tile):
        self.playerPool[player][tile] += 1
        self.orderedPool[player].append(tile)
    
    def decPlayerPool(self, player, tile):
        self.playerPool[player][tile] -= 1
        self.orderedPool[player].pop(tile)

    def addDoraIndicator(self, doraIndicator):
        self.orderedDora.append(doraIndicator)
        super().addDoraIndicator(doraIndicator)


    def handleMeld(self, player, meldInfo, isClosedCall):
        meldTiles = meldInfo[0]
        meldType = meldInfo[1]

        # (ordering of if and elif is important here)
        # handles chakan
        if meldType == 3: 
            self.decPlayerPonTiles(player, meldTiles)
            self.decPon(player)
            self.playerMelds[player][ meldTiles[0] ] = 4
            self.orderedMelds[player].pop(([meldTiles[0]*3],1))
            self.orderedMelds[player].add(([meldTiles[0]*4],1))
            self.addKan(player)
            self.privateHands[player][ meldTiles[0] ] = 0
       
        # handles closed kan       
        elif isClosedCall:
            self.privateHands[player][ meldTiles[0] ] = 0
            self.addKan(player)
            self.playerMelds[player][ meldTiles[0] ] = 4
            self.orderedMelds[player].add(([meldTiles[0]*4],0))

        # handles regular call
        else:
            self.setOpen(player)
            # adds meld tiles to meld attribute
            self.orderedMelds[player].add(meldTiles)

            for tile in meldTiles:
                self.playerMelds[player][tile] += 1 

            called = self.lastDiscardTile
            meldTiles.remove(called)  
            #removes tiles from player hand
            for tile in meldTiles:
                self.privateHands[player][tile] -= 1
            # adds pon if pon
            if meldType == 1:
                self.addPlayerPonTiles(player, meldTiles)
            # adds meld number
            self.addMeldNum(player, meldType)

    


gameData = GameData()

print(gameData.wallTiles)
