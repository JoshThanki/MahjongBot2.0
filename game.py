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

            if self.newGame:
                print("Starting a new game")
                # print(self.gameData)
            

            self.newGame = False

            self.drawStep()
            if self.checkOver():
                continue

            self.drawActionStep()

            if self.checkOver():
                continue

            self.discardStep()
            self.discardActionStep()

            if self.checkOver():
                continue

            time.sleep(5)
    
    # Have the given POV Player draw a tile    
    def drawStep(self):
        turnPlayer = self.gameData.playerTurn
        draw = self.gameData.getRandTile()
        if not draw:
            print("Game Draws")
            self.handleRyuukyoku()

        print(turnPlayer, "Draws: ", draw)

        self.gameData.handleDraw(turnPlayer, draw)
    
    # On Draw, a player can tsumo, riichi, closed kan or chakan. Handles the draw action a player can make
    def drawActionStep(self):
        turnPlayer = self.gameData.playerTurn
        action = self.players[turnPlayer].drawAction()

        #action = {actionType : (0-8) 0-Nothing, 1-TSUMO, 2-RIICHI, 3-CLOSEDKAN, 4-CHAKAN, 4-RON, 5-PON, 6-KAN, 7-CHI
        #, arr : [], player : (0-3)}
        actionType = action.type

        if actionType == 1:
            self.handleTsumo(turnPlayer)
            print(turnPlayer, "Declares: Tsumo: ")
        elif actionType == 2:
            self.handleRiichi(turnPlayer)
            print(turnPlayer, "Declares: Riichi: ")
        elif actionType == 3:
            self.handleCKAN(turnPlayer)
            print(turnPlayer, "Declares: Closed Kan: ")
        elif actionType == 4:
            self.handleCHAKAN(turnPlayer)
            print(turnPlayer, "Declares: ChaKan")


    # Have the given POV Player discard a tile   
    def discardStep(self):
        turnPlayer = self.gameData.playerTurn
        discard = self.players[turnPlayer].discard()
        print(turnPlayer, "Discards: ", discard)
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
        filtered_actions = [action for action in actionList if action.type != 0]

        # Sort the player actions based on a given priority (Ron -> Pon -> Kan -> Chii)
        filtered_actions.sort(key=lambda x: x.type)

        ronList = []

        if filtered_actions:

            for action in filtered_actions:
                if action.type == 5:
                    ronList.append(action)
                elif ronList:
                    self.handleRon([action.player for action in ronList],[action.arr[0] for action in ronList], fromPlayer=turnPlayer)

                    print([action.player for action in ronList], "Declare: Ron")

                    break

                elif action.type == 6 :
                    self.handlePon(action.player, fromPlayer=turnPlayer)
                    print(action.player, "Declares: Pon")

                    break

                elif action.type == 7:
                    self.handleKan(action.player, fromPlayer=turnPlayer)
                    print(action.player, "Declares: Kan")

                    break
                elif action.type == 8:
                    self.handleChi(action.player, action.arr, fromPlayer=turnPlayer)
                    print(action.player, "Declares: Chi")

                    break
                
        else:
            self.gameData.incPlayerTurn()

    def checkOver(self):
        return self.newGame


    def handleRyuukyoku(self):
        condition = 3

        newPoints = self.pointExchange(condition)

        self.newRound(newPoints)


    def handleTsumo(self, player):
        #condition TSUMO = 0, RON = 1,(For now)
        condition = 0

        newPoints = self.pointExchange(player, condition, fromPlayer = None)

        self.newRound(newPoints, player)


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

        self.newRound(newPoints, player)
    
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

        return [250] * 4 #random ahh point assingment
    
    def newRound(self, newPoints, winningPlayer = -1):
        
        #NOT IMPLEMENTING HONBA JUST YET
        print(newPoints)

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


