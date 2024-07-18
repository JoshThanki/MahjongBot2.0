import numpy as np
from gameData import GameData
import checkYaku 

#gameData, player, typeWin, tile

yakus = {}

# ONE HAN CLOSED ONLY

def Menzenchin_tsumohou(gameData, player, typeWin):
    if (typeWin==3) and (gameData.getClosed(player)):
        yakus[0] = 1

def Riichi(gameData, player):
    if gameData.getRiichi(player):
        yakus[1] = 1

#def Ippatsu(gameData, player):
    # Will do


def Pinfu(gameData, player, typeWin):
    if (gameData.getClosed(player)) and (checkYaku.getSeq() == 4):
        if checkYaku.getLastSet()[0] != 1 or checkYaku.getLastSet()[1] != 9:
            yakus[3] = typeWin
        


def Iipeikou(gameData, player):
    if (gameData.getClosed(player)):
        hand = checkYaku.checkYaku(gameData.privateHands[player])
        
        tuples = [tuple(trip) for trip in hand]

        count_set = {}
        duplicate_array = []

        for t in tuples:
            if t in count_set:
                count_set.remove(t)
                duplicate_array.append(t)  # Save the duplicate array
            else:
                count_set.add(t)

        if len(count_set) > 0:
            yakus[4] = len(count_set)
        

# ONE HAN



