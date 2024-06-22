import numpy as np
from numpy.typing import NDArray

from game import Game

class Player:
    def __init__(self, activeGame: Game) -> None:
        self.activeGame = activeGame
        self._readableHand = []
        for i in range(13):
            self.drawTile()
        self._vectorHand = Game.readableToVector(self.getReadableHand())
        self._readableHand = Game.vectorToReadable(self.getVectorHand()) #lazy way to sort the readable hand

    def drawTile(self):
        self._readableHand.append(self.activeGame.draw())
        self._vectorHand = Game.readableToVector(self._readableHand)
        self._readableHand = Game.vectorToReadable(self._vectorHand)

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