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
        self.gameData.buildMatrix(self.playerNo)
        prediction = model( np.array([self.gameData.getMatrix().flatten()]) )

        pred = prediction[0].numpy()
        hand = self.gameData.getPrivateHand(self.playerNo)

        filtered_prediction = [pred[i] if hand[i] != 0 else 0 for i in range(34)]

        return np.argmax(filtered_prediction)



    

