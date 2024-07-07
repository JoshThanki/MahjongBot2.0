from Global import *

from player import Player
from gameData import GameData


 #Creates a dictionary containing an entire set of tiles

class Game():
    
    def __init__(self):

        
        #points = [250,250,250,250] 
        #round = east
        #dealer = east
        #honba sticks = 0
        
        self.running = True
        self.newGame = True
        self.gameData = GameData() 

        self.players = [Player(i, self.gameData) for i in range(4)]

    def main(self):
        while self.running:
            self.newGame = False

            self.drawStep()
            self.drawActionStep()

            if self.newGame:
                continue

            self.discardStep()
            self.discardActionStep()
    

    def drawStep(self):
        turnPlayer = self.gameData.playerTurn
        draw = self.gameData.getRandTile()
        if not draw:
            self.handleRyuukyoku()

        self.gameData.handleDraw(turnPlayer, draw)
    
    def drawActionStep(self):
        turnPlayer = self.gameData.playerTurn
        action = self.players[turnPlayer].drawAction()

        #action = {actionType : (0-8) 0-Nothing, 1-TSUMO, 2-RIICHI, 3-CLOSEDKAN, 4-CHAKAN, 4-RON, 5-PON, 6-KAN, 7-CHI
        #, arr : [], player : (0-3)}
        actionType = action.type

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

        filtered_actions = [action for action in actionList if action.type != 0]

        filtered_actions.sort(key=lambda x: x.type)

        ronList = []

        for action in filtered_actions:
            if action['actionType'] == 5:
                ronList.append(action)
            elif ronList:
                self.handleRon([action["player"] for action in ronList],[action.arr[0] for action in ronList], fromPlayer=turnPlayer)
            
            elif action['actionType'] == 6 :
                self.handlePon(action["player"], fromPlayer=turnPlayer)

            elif action['actionType'] == 7:
                self.handleKan(action["player"], fromPlayer=turnPlayer)

            elif action['actionType'] == 8:
                self.handleChi(action["player"], action.arr, fromPlayer=turnPlayer)
            else:
                self.gameData.incPlayerTurn()


    def handleRyuukyoku(self):
        condition = 3

        newPoints = self.pointExchange(condition)


    def handleTsumo(self, player):
        #condition TSUMO = 0, RON = 1,(For now)
        condition = 0

        newPoints = self.pointExchange(condition, player)

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

        newPoints = self.pointExchange(condition, player, fromPlayer)

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

    

    #condition - 0 - TSUMO, 1 - RON , 3 - Ryuukyoku

    def pointExchange(self, condition, player = None, fromPlayer = None) :

        lastDraw = self.gameData.lastDrawTile
        lastDiscard = self.gameData.lastDiscardTile

        return [30] * 250 #random ahh point assingment
    
    def newRound(self, newPoints, winningPlayer = -1):
        
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
        
        self.newGame = True
        self.gameData = GameData(newPoints, newDealer, newRound, honbaSticks, eastOnly)
        self.players = [Player(i, self.gameData) for i in range(4)]

    def printScore(self, points):
        print(points)
        self.running = False




    
game = Game()
game.main()


