from Global import *
from gameData import GameData
from action import Action

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
        return self.gameData.lastDrawTile
    

