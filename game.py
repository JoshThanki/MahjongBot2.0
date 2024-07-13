from Global import *

from player import Player
from gameData import GameData
import tensorflow as tf

class Game():
    
    def __init__(self):

        
        #points = [250,250,250,250] 
        #round = east
        #dealer = east
        #honba sticks = 0 

        #uncomment this line to print to out

        self.file = open("out.txt", "w+") 
        # self.file = None

        self.running = True
        self.newGame = True
        self.gameData = GameData(eastOnly=True) 

        # Comment this to test specific functions
        models = [tf.keras.models.load_model('Saved Models\discardModel'), tf.keras.models.load_model('Saved Models\discardModel'), tf.keras.models.load_model('Saved Models\chiModel'), tf.keras.models.load_model('Saved Models\ponModel'), tf.keras.models.load_model('Saved Models\kanModel') ]
        
        self.players = [Player(i, self.gameData, models=models) for i in range(4)] 

    def main(self):
        
        
        while self.running:
            
            if self.newGame:
                print("Starting a new game", file=self.file)
                # print(self.gameData)
            
            self.newGame = False

            self.drawStep()
            self.drawActionStep()

            if self.checkOver():
                continue

            self.gameData.printGood(self.gameData.playerTurn, self.file)

            self.discardStep()

            self.gameData.printGood(self.gameData.playerTurn, self.file)

            self.discardActionStep()

            if self.checkOver():
                continue
            

    
    # Have the given POV Player draw a tile    
    def drawStep(self):
        turnPlayer = self.gameData.playerTurn
        draw = self.gameData.getRandTile()
        
        print(f"\n{turnPlayer} Draws:  {tile_dic[draw]}", file=self.file)

        self.gameData.handleDraw(turnPlayer, draw)
    
    # On Draw, a player can tsumo, riichi, closed kan or chakan. Handles the draw action a player can make
    def drawActionStep(self):
        turnPlayer = self.gameData.playerTurn
        action = self.players[turnPlayer].drawAction()

        #action = {actionType : (0-8) 0-Nothing, 1-TSUMO, 2-RIICHI, 3-CLOSEDKAN, 4-CHAKAN, 4-RON, 5-PON, 6-KAN, 7-CHI
        #, arr : [], player : (0-3)}
        actionType = action.type

        print(f"\nDraw Action type: {actionType}", file=self.file)

        if actionType == 1:
            self.handleTsumo(turnPlayer)
            
        elif actionType == 2:
            self.handleRiichi(turnPlayer)
            
        elif actionType == 3:
            self.handleCKAN(turnPlayer, action.arr[0])
            
        elif actionType == 4:
            self.handleCHAKAN(turnPlayer, action.arr[0])
            


    # Have the given POV Player discard a tile   
    def discardStep(self):
        turnPlayer = self.gameData.playerTurn
        discard = self.players[turnPlayer].discard()
        print(turnPlayer, "Discards: ", tile_dic[discard], file=self.file)
        self.gameData.handleDiscard(turnPlayer, discard)
        self.gameData.addPlayerPool(turnPlayer, discard)
    
    # On Discard, all other players can chii, pon, kan or ron. Handles the discard actions a player can make
    def discardActionStep(self):

        # Get all players that arent the POV player as a list 
        turnPlayer = self.gameData.playerTurn
        otherPlayers = [0,1,2,3]
        otherPlayers.remove(turnPlayer)

        #action = {actionType : (0-8) 0-Nothing, 1-TSUMO, 2-RIICHI, 3-CLOSEDKAN, 4-CHAKAN, 5-RON, 6-PON, 7-KAN, 8-CHI
        #, arr : [], player : (0-3)}
        
        # Get the discard actions of the players that choose to actually take an action (0 indicates the player does nothing)
        actionList = [self.players[player].discardAction() for player in otherPlayers]

        # Sort the player actions based on a given priority (Ron -> Pon -> Kan -> Chii)

        ronList = [action for action in actionList if action.type == 5]

        otherActions = [action for action in actionList if action.type != 5 and action.type !=0]

        otherActions.sort(key=lambda x: x.type)
    
        formatActionList = lambda actionList: [f"Type: {action.type}, player: {action.player}, fromPlayer: {turnPlayer}, last Discard: {self.gameData.lastDiscardTile}" for action in actionList]

        print(f"Discard Step Actions: Ron list: {formatActionList(ronList)} ,  Other Actions: {formatActionList(otherActions)}", file=self.file)

        if ronList:

            self.handleRon([action.player for action in ronList], fromPlayer=turnPlayer)
        
        elif otherActions:

            if otherActions[0].type == 6 :
                self.handlePon(otherActions[0].player, fromPlayer=turnPlayer)    

            elif otherActions[0].type == 7:
                self.handleKan(otherActions[0].player, fromPlayer=turnPlayer)
                
            elif otherActions[0].type == 8:
                self.handleChi(otherActions[0].player, otherActions[0].arr, fromPlayer=turnPlayer)

            else:
                print("Unknown Action Type")
            
        
        else:
            self.gameData.incPlayerTurn()



        self.gameData.incTurnNumber()
        self.checkRyuukyoku()



    def checkOver(self):
        return self.newGame or not self.running


    def checkRyuukyoku(self):
        if self.gameData.getWallTiles() == 0:
            
            print("Game Draws", file=self.file)

            condition = 3

            tempaiPlayers = []
            nonTempaiPlayers = []

            for i in range(0,3):
                hand = self.gameData.privateHands[i]
                if calcShanten(hand) == 1: # Shanten being 1 means the player is in tenpai
                    tempaiPlayers.append(i)
                else:
                    nonTempaiPlayers.append(i)

            newPoints = self.pointExchange(condition, tempaiPlayers, nonTempaiPlayers)

            self.newRound(newPoints)


    def handleTsumo(self, player):
        #condition TSUMO = 0, RON = 1, DRAW = 3 (For now)
        condition = 0

        newPoints = self.pointExchange(condition, player)

        print(player, "Declares: Tsumo: ", file=self.file)

        self.newRound(newPoints, player)


    def handleRiichi(self, player):

        print(player, "Declares: Riichi: ", file=self.file)

        self.gameData.setRiichi(player)

    def handleCKAN(self, player, tile):
        meld = [[tile]*4, 3]

        self.gameData.handleMeld(player, meld)

        print(player, "Declares: Closed Kan: ", file=self.file)

        self.drawStep()
        self.drawActionStep()


    def handleCHAKAN(self, player, tile):
        meld = [[tile]*4, 4]

        print(player, "Declares: ChaKan", file=self.file)

        self.gameData.handleMeld(player, meld)

        self.drawStep()
        self.drawActionStep()

    #players - [player], #from-player - [player]
    def handleRon(self, players, fromPlayer):
        #condition TSUMO = 0, RON = 1,(For now)
        lastDiscard = self.gameData.lastDiscardTile

        condition = 1

        newPoints = self.pointExchange(condition, players, fromPlayer)

        print(f"Player(s) {players} Declare: Ron, On tile: {lastDiscard}, From Player: {fromPlayer}", file=self.file)

        #For now just take the first ron player
        winningPlayer = self.gameData.roundDealer if self.gameData.roundDealer in players else players[0]

        self.newRound(newPoints, winningPlayer)
    
    def handlePon(self, player, fromPlayer):
        discard = self.gameData.lastDiscardTile

        meld = [[discard]*3, 1]

        print(player, "Declares: Pon", file=self.file)
        
        self.gameData.handleMeld(player, meld, fromPlayer = fromPlayer)
        
        self.gameData.setPlayerTurn(player)

        self.discardStep()
        self.discardActionStep()

    def handleKan(self, player, fromPlayer):
        discard = self.gameData.lastDiscardTile

        meld = [[discard]*3, 2]
        
        print(player, "Declares: Open Kan", file=self.file)
        
        self.gameData.handleMeld(player, meld, fromPlayer = fromPlayer)

        self.gameData.setPlayerTurn(player)



        self.drawStep()
        self.drawActionStep()

    def handleChi(self, player, tileList, fromPlayer):
        
        tileList.sort()

        meld = [tileList, 0]

        print(player, "Declares: Chi", file=self.file)

        self.gameData.handleMeld(player, meld, fromPlayer = fromPlayer)

        self.gameData.setPlayerTurn(player)

        self.discardStep()
        self.discardActionStep()


    def pointExchange(self, condition, player = None , fromPlayer = None):

        arrPoints = self.gameData.getPlayerScores()

        #condition TSUMO = 0, RON = 1, DRAW = 3 (For now)
        if condition == 3:
            #player [player]
            #fromPlayer [player]
            tPointer = 0
            fPointer = 0

            if player:
                pointsToGive = 30 / len(player)

                while (fPointer < len(fromPlayer) and tPointer < len(player)):
                    if fPointer < len(fromPlayer): 
                        arrPoints[fPointer] -= pointsToGive
                        fPointer += 1 
                    if tPointer < len(player):
                        arrPoints[tPointer] += pointsToGive 
                        tPointer += 1
        

        elif condition == 1:
            #player [player]
            #fromPlayer (0-3)

            totalPoints = 30  #Point calc required


            pointsToGive = totalPoints
            for p in player:
                arrPoints[fromPlayer] -= pointsToGive
                arrPoints[p] += pointsToGive
            

        elif condition == 0:
            #player (0-3)
            #fromPlayer None
            
            totalPoints = 30 #Point calc required

            otherPlayers = [i for i in range(4)]
            otherPlayers.remove(player)

            pointsToGive = totalPoints // len(otherPlayers)

            for p in otherPlayers:
                arrPoints[p] -= pointsToGive
                arrPoints[player] += pointsToGive


        return arrPoints
    
    def newRound(self, newPoints, winningPlayer = -1):
        
        #NOT IMPLEMENTING HONBA JUST YET
        print(newPoints, file=self.file)

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
        for player in self.players:
            player.updateGameData(self.gameData)
        

    def printScore(self, points):
        self.running = False


    
game = Game()

start = time.time()
game.main()
end = time.time()
print(f"Time: {end - start}")

