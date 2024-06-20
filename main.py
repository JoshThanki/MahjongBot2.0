import json
import random
import numpy as np


with open('tiles.json', 'r') as file:
    start_tiles = json.load(file) #Creates a dictionary containing an entire set of tiles

class Game:
    def __init__(self):

        self.gameState = np.zeros((11, 34))
