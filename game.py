import json
import random
import numpy as np
from numpy.typing import NDArray
from Global import *
from player import Player
from matrix import Matrix

 #Creates a dictionary containing an entire set of tiles

class Game():
    
    def __init__(self):

        
        #points = [250,250,250,250] 
        #round = east
        #dealer = east
        #honba sticks = 0
        
        self.running = True
        self.gameData = GameData() 
        self.gameData.buildMatrix(0)
        print(self.gameData)

        self.players = [Player(i) for i in range(4)]

    
    def drawStep(self):
        turnPlayer = self.gameData.playerTurn
        draw = self.gameData.getRandTile()
        self.gameData.handleDraw(turnPlayer, draw)
    
    def drawActionStep(self):
        turnPlayer = self.gameData.playerTurn
        action = self.players[turnPlayer].drawAction()

        #action = {actionType : (0-8) 0-Nothing, 1-TSUMO, 2-RIICHI, 3-CLOSEDKAN, 4-CHAKAN, 4-RON, 5-PON, 6-KAN, 7-CHI
        #, arr : [], player : (0-3)}
        actionType = action[0]

        if actionType == 1:
            self.handleTsumo(turnPlayer)
        elif actionType == 2:
            self.handleRiichi(turnPlayer)
        elif actionType == 3:
            self.handleCKAN(turnPlayer)
        elif actionType == 4:
            self.handleCHAKAN(turnPlayer)


    def discardStep(self):
        turnPlayer = self.gameData.playerTurn
        discard = self.players[turnPlayer].discard()
        self.gameData.handleDiscard(turnPlayer, discard)
        self.gameData.addPlayerPool(turnPlayer, discard)
    
    def discardActionStep(self):
        turnPlayer = self.gameData.playerTurn
        otherPlayers = [0,1,2,3]
        otherPlayers.remove(turnPlayer)

        #action = {actionType : (0-8) 0-Nothing, 1-TSUMO, 2-RIICHI, 3-CLOSEDKAN, 4-CHAKAN, 5-RON, 6-PON, 7-KAN, 8-CHI
        #, arr : [], player : (0-3)}

        actionList = [self.players[player].discardAction() for player in otherPlayers]

        filtered_actions = [action for action in actionList if action['actionType'] != 0]

        filtered_actions.sort(key=lambda x: x['actionType'])

        ronList = []

        for action in filtered_actions:
            if action['actionType'] == 5:
                ronList.append(action)
            elif ronList:
                self.handleRon([action["player"] for action in ronList],[action["arr"][0] for action in ronList], fromPlayer=turnPlayer)
            
            elif action['actionType'] == 6 :
                self.handlePon(action["player"], fromPlayer=turnPlayer)

            elif action['actionType'] == 7:
                self.handleKan(action["player"], fromPlayer=turnPlayer)

            elif action['actionType'] == 8:
                self.handleChi(action["player"], action["arr"], fromPlayer=turnPlayer)
            else:
                self.gameData.incPlayerTurn()


    def handleTsumo(self, player):
        #condition TSUMO = 0, RON = 1,(For now)
        condition = 0

        newPoints = self.pointExchange(player, condition, fromPlayer = None)

        self.gameData.newRound(newPoints, player)


    def handleRiichi(self, player):

        self.gameData.setRiichi(player)

    def handleCKAN(self, player, tile):
        drawTile = self.gameData.lastDrawTile
        meld = [[drawTile]*4, 2]

        self.gameData.handleMeld(player, meld, isClosedCall=True)

    def handleCHAKAN(self, player, tile):
        drawTile = self.gameData.lastDrawTile

        meld = [[drawTile]*3, 3]
        
        self.gameData.handleMeld(player, meld)

    def handleRon(self, player, fromPlayer):
        #condition TSUMO = 0, RON = 1,(For now)
        condition = 1

        newPoints = self.pointExchange(player, condition, fromPlayer)

        self.gameData.newRound(newPoints, player)
    
    def handlePon(self, player, fromPlayer):
        discard = self.gameData.lastDiscardTile

        meld = [[discard]*3, 1]
        
        self.gameData.handleMeld(player, meld, fromPlayer = fromPlayer)

    def handleKan(self, player, fromPlayer):
        discard = self.gameData.lastDiscardTile

        meld = [[discard]*3, 2]
        
        self.gameData.handleMeld(player, meld, fromPlayer = fromPlayer)

    def handleChi(self, player, tileList, fromPlayer):

        meld = [tileList, 3]
    
        self.gameData.handleMeld(player, meld, fromPlayer = fromPlayer)


    def pointExchange(self, player, condition, fromPlayer):
        lastDraw = self.gameData.lastDrawTile
        lastDiscard = self.gameData.lastDiscardTile

        return [30] * 250 #random ahh point assingment
    
    def newRound(self, newPoints, winningPlayer):
        
        #NOT IMPLEMENTING HONBA JUST YET

        oldDealer = self.gameData.roundDealer
        eastOnly = self.gameData.eastOnly
        honbaSticks = self.gameData.honbaSticks
        newRound = self.gameData.roundWind

        if not (oldDealer == winningPlayer):
            newDealer = oldDealer + 1
    
        else:
            newDealer = oldDealer
        
        if newDealer > 3:
            if eastOnly:
                self.printScore(newPoints)
            elif self.gameData.roundWind == 1:
                self.printScore(newPoints)
            else:
                newRound+=1
                newDealer = 0
        
        self.gameData = GameData(newPoints, newDealer, newRound, honbaSticks, eastOnly)

    def printScore(self, points):
        print(points)
        self.running = False


#Class used to store all data about the game

class GameData(Matrix):
    
    #points [1,2,3,4], dealer (0-3), roundWind (0-3) honbaSticks (int)

    def __init__(self, points = [250,250,250,250], dealer = 0, roundWind = 0, honbaSticks = 0, eastOnly = False):
        
        ### Define Variables ###

        with open('tiles.json', 'r') as file:
            start_tiles = json.load(file)

        self.eastOnly = eastOnly

        self.playerTurn = dealer 

        #self.orderedMelds = [[([5,6,7],1) , ([5,5,5],1) , [] ],[],[],[]]
        self.orderedMelds = [[],[],[],[]]

        #self.orderedPool = [[1,2,4,6],[],[],[]]
        self.orderedPool = [[],[],[],[]]

        self.orderedDora = []

        super().__init__()

        ### Initialise Game ###

        self.tilePool = start_tiles
            
        initialHands = [self.convertHandFormat([self.getRandTile() for i in range(13)]) for j in range(4)]
        
        #sets points
        self.setPlayerScore(points)
        
        #sets player winds
        self.setDealer(dealer)
        self.setPlayerWinds()

        #sets starting hands
        self.initialisePrivateHands(initialHands)

        #sets more metadata form seed
        
        self.setHonbaSticks(honbaSticks)
        self.setRoundWind(roundWind)
        self.newDora()


        
    def incPlayerTurn(self):
        self.playerTurn = (self.playerTurn + 1) % 3

    def convertHandFormat(self, hand):
        newHand = [0] * 34
        for tile in hand:
            newHand[tile] += 1
        
        return newHand


    def getRandTile(self):
        keys, weights = zip(*self.tilePool.items())

        if any(weights):
            tempRandomElement = random.choices(keys, weights=weights)[0]
            self.tilePool[tempRandomElement] -= 1
            return int(tempRandomElement)
        
        else:
            return None

    def getNumKans(self):
        sum(self.kansNum)

    def newDora(self):
        dora = self.getRandTile()
        self.addDoraIndicator(dora)


    ### Overriden Methods ### 

    def addPlayerPool(self, player, tile):
        self.playerPool[player][tile] += 1
        self.orderedPool[player].append(tile)
    
    def decPlayerPool(self, player, tile):
        self.playerPool[player][tile] -= 1
        self.orderedPool[player].pop(tile)

    def addDoraIndicator(self, doraIndicator):
        self.orderedDora.append(doraIndicator)
        super().addDoraIndicator(doraIndicator)


    def __str__(self):
        return self.get_all_attributes()
    
    def get_all_attributes(self):
        attributes = {}
        current_class = self.__class__
        
        # Traverse through the MRO (Method Resolution Order)
        for cls in current_class.__mro__:
            if cls == object:
                continue  # Skip the base 'object' class
            # Get instance attributes if the current object is an instance of the class
            if '__dict__' in cls.__dict__:
                attributes.update(self.__dict__)

        # Format attributes manually
        def format_value(value):
            if isinstance(value, np.ndarray):
                if value.ndim == 1:
                    return '[' + ', '.join(map(str, value.tolist())) + ']'
                elif value.ndim == 2:
                    return '[\n ' + ',\n '.join(['[' + ', '.join(map(str, row.tolist())) + ']' for row in value]) + '\n]'
            return repr(value)

        formatted_attributes = []
        for key, value in attributes.items():
            formatted_attributes.append(f'    "{key}": {format_value(value)}')

        formatted_string = "{\n" + ",\n".join(formatted_attributes) + "\n}"
        return f'{self.__class__.__name__}:\n{formatted_string}'
    
    def handleMeld(self, player, meldInfo, isClosedCall=False, fromPlayer = None):
        meldTiles = meldInfo[0]
        meldType = meldInfo[1]

        # (ordering of if and elif is important here)
        # handles chakan
        if meldType == 3: 
            self.decPlayerPonTiles(player, meldTiles)
            self.decPon(player)
            self.playerMelds[player][ meldTiles[0] ] = 4
            self.orderedMelds[player].pop(([meldTiles[0]*3],1))
            self.orderedMelds[player].add(([meldTiles[0]*4],1))
            self.addKan(player)
            self.privateHands[player][ meldTiles[0] ] = 0
       
        # handles closed kan       
        elif isClosedCall:
            self.privateHands[player][ meldTiles[0] ] = 0
            self.addKan(player)
            self.playerMelds[player][ meldTiles[0] ] = 4
            self.orderedMelds[player].add(([meldTiles[0]*4],0))

        # handles regular call
        else:
            lastDiscard = self.lastDiscardTile
            self.setOpen(player)
            # adds meld tiles to meld attribute
            self.orderedMelds[player].add(meldTiles)
            self.decPlayerPool(fromPlayer, lastDiscard) 

            for tile in meldTiles:
                self.playerMelds[player][tile] += 1 

            called = self.lastDiscardTile
            meldTiles.remove(called)  
            #removes tiles from player hand
            for tile in meldTiles:
                self.privateHands[player][tile] -= 1
            # adds pon if pon
            if meldType == 1:
                self.addPlayerPonTiles(player, meldTiles)
            # adds meld number
            self.addMeldNum(player, meldType)

    


