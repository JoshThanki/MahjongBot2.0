from game import Game
from player import Player

testGame = Game()
player1 = Player(testGame)

if True: #add tests here
    print(player1.getReadableHand())
    print(player1.getVectorHand())