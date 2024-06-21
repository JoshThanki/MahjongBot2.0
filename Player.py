import numpy as np
from numpy.typing import NDArray

import Game

class Player:
    def __init__(self, readableHand: list) -> None:
        self.readableHand = readableHand
        self.vectorHand = Game.readableToVector(self.readableHand)
        pass