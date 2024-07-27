from Global import *
from gameData import GameData
from action import Action
from pathlib import Path

from buffer import Buffer

#action = actionType : (0-8) 0-Nothing, 1-TSUMO, 2-RIICHI, 3-CLOSEDKAN, 4-CHAKAN, 4-RON, 5-PON, 6-KAN, 7-CHI
        #, arr : [], player : (0-3)

#discard returns tile (0-33)

class MPlayer:
    def __init__(self, playerNo, gameData: GameData, buffer : Buffer) -> None:
        self.gameData = gameData
        self.playerNo = playerNo
        self.buffer = buffer

    def updateGameData(self, gameData):
        self.gameData = gameData
        
    def getPredictionMeld(self, model):
        state = self.gameData.getMatrix()
        prediction = model( np.array([state.flatten()]) )

        prediction = prediction[0].numpy()

        return np.argmax(prediction)   
    
    
    def getPredictionDiscard(self):
        hand = self.gameData.getPrivateHand(self.playerNo)
        
        tile = None


        if self.gameData.getRiichi(self.playerNo):
            action, player = self.gameData.getLastDrawAction()

            

            if action == 2 and player == self.playerNo:
                meldNo = self.gameData.getMeldNum(self.playerNo)
            
                def simDiscard(hand, discard):
                    hand[discard] -= -1
                    return hand

                shantenDiscards = [calcShanten(simDiscard(hand[:], tile), meldNo)  if tileCount > 0 else None for tile, tileCount in enumerate(hand)]

                tile = self.buffer.request(0,[1 if shantenDiscards[i] == 0 else 0 for i in range(34)])[0]

            else:

                return self.gameData.lastDrawTile
            
        if not tile:

            tile = self.buffer.request(0,hand)[0]

        return tile

    def canTsumo(self):
        return self.gameData.totalHandShanten( self.playerNo ) == -1
 

    def canRon(self):
        copyHand = copy.copy( self.gameData.privateHands[ self.playerNo ] )
        copyHand[ self.gameData.lastDiscardTile ] +=1

        numCalledMelds = self.gameData.getMeldNum( self.playerNo )

        return calcShanten( hand=copyHand, numCalledMelds=numCalledMelds ) == -1 


    # returns an array of possible chis which are represented by the base tile (lowest tile in the chi)
    def possibleChis(self):
        tile = self.gameData.lastDiscardTile
        hand = self.gameData.privateHands[ self.playerNo ]

        if tile//9 == 3: return False

        tileNum = tile%9

        tile0 = hand[tile-2]>0 if tile>=2 else False 
        tile1 = hand[tile-1]>0 if tile>=1 else False
        tile2 = hand[tile+1]>0
        tile3 = hand[tile+2]>0

        possibleChis = []

        if tile0 and tile1 and (tileNum>=2):
            possibleChis.append(tile-2)

        if tile1 and tile2 and (tileNum%8 != 0):
            possibleChis.append(tile-1)

        if tile2 and tile3 and (tileNum <= 6):
            possibleChis.append(tile)

        return possibleChis   


    def bestChi(self):
        currenthand = self.gameData.privateHands[ self.playerNo ]
        calledTile = self.gameData.lastDiscardTile 

        resMeldNum = self.gameData.getMeldNum( self.playerNo )+1    
    
        minShanten = 128
        bestChiBase = None

        for chiBaseTile in self.possibleChis():
            curShanten = calcShanten(hand=self.handAfterChi(currenthand, chiBaseTile, calledTile),  numCalledMelds=resMeldNum)

            if curShanten < minShanten:
                minShanten = curShanten
                bestChiBase = chiBaseTile

        return bestChiBase
    
    def handAfterChi(self, hand, chiBase, called):
        handCopy= copy.copy(hand)

        chiTiles = [chiBase,chiBase+1,chiBase+2]
        chiTiles.remove(called)

        for i in chiTiles:
            handCopy[i] -= 1

        return handCopy
             


    def drawAction(self):
        actionList = []

        res = Action(self.playerNo, 0)
        
        if self.canTsumo():

            actionList.append(Action(self.playerNo, 1))
        
        
        #canClosedkan returns (CanClosedKan, Call Tile)
        if self.gameData.canClosedKan(self.playerNo)[0]:
            callTile = self.gameData.canClosedKan( self.playerNo )[1]

            actionList.append(Action(self.playerNo, 3, [callTile]))      

        
        if self.gameData.canChakan( self.playerNo )[0]:
            callTile = self.gameData.canChakan( self.playerNo )[1]

            actionList.append(Action(self.playerNo, 4, [callTile]))


        if self.gameData.canRiichi(self.playerNo):
            actionList.append(Action(self.playerNo, 2))
        
        if actionList:
            actionList.append(Action(self.playerNo, 0))
            res = self.buffer.request(1, actionList)[0]
    
        return res



    def discardAction(self):
        actionList = []

        res = Action(self.playerNo, 0)
    
        if self.canRon():
            actionList.append((self.playerNo, 5))
        
        if self.gameData.canChi(self.playerNo):

            actionList.append(Action(self.playerNo, 8, [int(self.bestChi()) + i for i in range(3)]))
            
        if self.gameData.canPon(self.playerNo):

            actionList.append(Action(self.playerNo, 6))

        if self.gameData.canKan(self.playerNo):

            actionList.append(Action(self.playerNo, 7))  
            
        if actionList:
            actionList.append(Action(self.playerNo, 0))
            res = self.buffer.request(1, actionList)[0]
    
        return res
       


    def discard(self):
        self.gameData.buildMatrix(self.playerNo)
        prediction = self.getPredictionDiscard()

        return prediction



    

