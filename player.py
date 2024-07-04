import numpy as np
from numpy.typing import NDArray

from game import GameData

class Player:
    def __init__(self, playerNo, gameData: GameData) -> None:
        self.gameData = gameData
        self.playerNo = playerNo
        self.discardTile = -1

    def discard(self):

    def getReadableHand(self):
        return self._readableHand
    
    def getVectorHand(self):
        return self._vectorHand

if True: #add tests here
    testGame = Game()
    testPlayer = Player(testGame)
    print(testPlayer.getReadableHand())
    print()
    print(testPlayer.getVectorHand())
    print()
    testPlayer.drawTile()
    print(testPlayer.getReadableHand())
    print()
    print(testPlayer.getVectorHand())