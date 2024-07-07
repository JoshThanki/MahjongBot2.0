from Global import *
from gameData import GameData
from action import Action

from pathlib import Path
import tensorflow as tf
import keras


#action = actionType : (0-8) 0-Nothing, 1-TSUMO, 2-RIICHI, 3-CLOSEDKAN, 4-CHAKAN, 4-RON, 5-PON, 6-KAN, 7-CHI
        #, arr : [], player : (0-3)

#discard returns tile (0-33)

class Player:
    def __init__(self, playerNo, gameData: GameData) -> None:
        self.gameData = gameData
        self.playerNo = playerNo
        self.discardTile = -1

    def drawAction(self):
        action = Action(self.playerNo)

        return action

    def discardAction(self):
        action = Action(self.playerNo)

        return action
    
    def discard(self):
        model = tf.keras.models.load_model('Saved Models\discardModel')
        gameData.buildMatrix(player)
        prediction = model( np.array([gameData.getMatrix(player).flatten()]) )
        return np.argmax(prediction)
    

