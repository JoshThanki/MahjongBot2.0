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

    def getReadableHand(self):
        return self._readableHand
    
    def getVectorHand(self):
        return self._vectorHand