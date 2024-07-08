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



class Player:
    def __init__(self, playerNo, gameData: GameData) -> None:
        self.gameData = gameData
        self.playerNo = playerNo
        self.discardTile = -1


        self.discardModel = tf.keras.models.load_model('Saved Models\discardModel')
        self.riichiModel = tf.keras.models.load_model('Saved Models\discardModel')   ##############
        self.chiModel = tf.keras.models.load_model('Saved Models\chiModel')
        self.ponModel = tf.keras.models.load_model('Saved Models\ponModel')
        self.kanModel = tf.keras.models.load_model('Saved Models\kanModel')    

    def getPrediction(self, model):
        state = self.gameData.gameState
        prediction = model( np.array([state.flatten()]) )

        prediction = prediction[0].numpy()

        if model == discardModel:
            hand = self.gameData.getPrivateHand(self.playerNo)
            prediction = [prediction[i] if hand[i] != 0 else 0 for i in range(34)]

        return np.argmax(prediction)   

    def canTsumo(self):
        return self.gameData.totalHandShanten( self.playerNo ) == -1
 

    def canRon(self, player):
        copyHand = copy.copy( self.gameData.privateHands[ self.playerNo ] )
        copyHand[ self.gameData.lastDiscardTile ] +=1

        numCalledMelds = self.gameData.getOpenMeldNum( self.playerNo )

        return calcShanten( hand=copyHand, numCalledMelds=numCalledMelds ) == -1 


    def drawAction(self):
        player = self.playerNo

        meldNum = self.gameData.getOpenMeldNum( player )
        hand = self.gameData.getPrivateHand( player )

        if self.canTsumo():
            action = Action(self.playerNo, 1)


        elif self.gameData.canClosedKan(player)[0] or self.gameData.canClosedKan(self.playerNo)[0]:   #placeholder
            self.gameData.buildMatrix( player=self.playerNo, forMeld=True, forClosedMeld=True, callTile=0 )
            matrix = self.gameData.getMatrix()
            prediction = self.getPrediction( self.kanModel )

            if prediction:
                return Action(self.playerNo, 3)        
        
        if self.gameData.canChakan( self.playerNo )[0]:
            callTile = self.gameData.canChakan( self.playerNo )[1]
            self.gameData.buildMatrix( player=self.playerNo, forMeld=True, forClosedMeld=True, callTile=callTile )
          
            prediction = self.getPrediction( self.kanModel )
            
            if prediction:
                return Action(self.playerNo, 4)  


        elif self.gameData.canRiichi(player):
            self.gameData.buildMatrix(player)
            matrix = self.gameData.getMatrix()
            prediction = self.getPrediction( self.riichiModel  )

            if prediction:
                return Action(self.playerNo, 2)
            

        return Action(self.playerNo, 0)


    def discardAction(self):
        if self.canRon(self.playerNo):
            return Action(self.playerNo, 4)
        
        if self.gameData.canChi(self.playerNo):
            self.gameData.buildMatrix( player=self.playerNo, forMeld=True )
            prediction = self.getPrediction( self.chiModel )

            if prediction:
                return Action(self.playerNo, 7)
            
        if self.gameData.canPon(self.playerNo):
            self.gameData.buildMatrix( player=self.playerNo, forMeld=True )
            prediction = self.getPrediction( self.ponModel )

            if prediction:
                return Action(self.playerNo, 5)   

        if self.gameData.canKan(self.playerNo):
            self.gameData.buildMatrix( player=self.playerNo, forMeld=True )
            prediction = self.getPrediction( self.kanModel )

            if prediction:
                return Action(self.playerNo, 6)  
            
        return Action(self.playerNo, 0)
       


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



    

