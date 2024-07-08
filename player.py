from Global import *
from gameData import GameData
from action import Action

from pathlib import Path
import tensorflow as tf
import keras


#action = actionType : (0-8) 0-Nothing, 1-TSUMO, 2-RIICHI, 3-CLOSEDKAN, 4-CHAKAN, 4-RON, 5-PON, 6-KAN, 7-CHI
        #, arr : [], player : (0-3)

#discard returns tile (0-33)

discardModel = tf.keras.models.load_model('Saved Models\discardModel')
riichiModel = tf.keras.models.load_model('Saved Models\discardModel')   ##############
chiModel = tf.keras.models.load_model('Saved Models\chiModel')
ponModel = tf.keras.models.load_model('Saved Models\ponModel')
kanModel = tf.keras.models.load_model('Saved Models\kanModel')

def getPrediction(model, state):
    prediction = model( np.array([ state.flatten() ]) )
    return np.argmax(prediction)



class Player:
    def __init__(self, playerNo, gameData: GameData) -> None:
        self.gameData = gameData
        self.playerNo = playerNo
        self.discardTile = -1

    def drawAction(self):
        meldNum = self.gameData.getOpenMeldNum(playerNo)
        hand = self.gameData.getPrivateHand(playerNo)

        if canWin(player):
            action = Action(self.playerNo, 1)


        elif canClosedKan(player) or canChakan(player):   #placeholder
            self.gameData.buildMatrix( player=playerNo, forMeld=True, forClosedMeld=True, callTile=0 )
            matrix = self.gameData.getMatrix( player )
            prediction = getPrediction( kanModel, matrix )

            if prediction:
                action = Action(self.playerNo, 3,)

        elif self.gameData.canRiichi(player):
            action = Action(self.playerNo, 2)
            self.gameData.buildMatrix( player=playerNo )
            matrix = self.gameData.getMatrix(player)
            prediction = getPrediction(riichiModel, matrix)

            if prediction:
                action = Action(self.playerNo, 2)
            
        else:
            action = Action(self.playerNo, 0)

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



    

