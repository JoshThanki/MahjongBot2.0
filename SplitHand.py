import numpy as np
from itertools import combinations

from gameData import GameData

# returns an array of groups in the hand
def getGroups(gameData, player):
    hand = gameData.privateHands[player]

    manTriplets = [[tile]*3 for tile in range(9) if hand[tile]>=3]
    pinTriplets = [[tile]*3 for tile in range(9,18) if hand[tile]>=3]
    souTriplets = [[tile]*3 for tile in range(18,27) if hand[tile]>=3]
    honourTriplets = [[tile]*3 for tile in range(27,34) if hand[tile]>=3]

    manSequences = []
    pinSequences = []
    souSequences = []

    tilePresence = lambda tile, tileAmount: (hand[tile]>=tileAmount) and (hand[tile+1]>=tileAmount) and (hand[tile+2]>=tileAmount)
    for index in range(7):
        manTemp = True
        souTemp = True
        pinTemp = True
        
        for numSeq in [4,3,2,1]:
            tile = index
            if manTemp and tilePresence(tile, numSeq):
                manSequences += [[tile,tile+1,tile+2]]*numSeq 
                manTemp = False

            tile = index + 9
            if pinTemp and tilePresence(tile, numSeq):
                pinSequences += [[tile,tile+1,tile+2]]*numSeq 
                pinTemp = False

            tile = index + 18
            if souTemp and tilePresence(tile, numSeq):
                souSequences += [[tile,tile+1,tile+2]]*numSeq 
                souTemp = False

    return manTriplets+manSequences+pinTriplets+pinSequences+ souTriplets+souSequences+honourTriplets



def findWinningHandSplits(gameData, player, typeWin):
    if typeWin == 5:
        gameData.addTilePrivateHand(gameData.lastDiscardTile)

    hand = gameData.privateHands[player]
    print(hand)
    groups = getGroups(gameData, player)
    GroupsToFind = 4 - gameData.getMeldNum(player)

    validCombinations = []
    for combination in combinations(groups, GroupsToFind):
        out = np.zeros(34, dtype=int)        
        for group in combination:
            validCombinations.append(group)
            for tile in group:
                out[tile]+=1

        if np.all(out <= hand) and np.isin(2, hand-out):
            pair_tile_index = (hand - out).tolist().index(2)
            validCombinations.append(pair_tile_index)

    
    return validCombinations


def Fu(gameData, player):
    winningTile = 5###
    fu = 20

    privHandSplit = findWinningHandSplits(gameData, player)
    for group in privHandSplit[:-1]:
        
        if group[0] == group[1]:
            if group[0] >= 27:
                fu += 8
            else:
                fu += 4

    pair = privHandSplit[-1]
    isPairWindYakuhai = (gameData.roundWind == pair) or (gameData.playerWinds[player] == pair)
    isPairDragYakuhai = (pair >= 31)
    
    if isPairWindYakuhai or isPairDragYakuhai:
        fu += 2

    return fu

hand = [0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 3, 0]
hand = [0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0]

gamedata = GameData()
print(gamedata.privateHands)

print(findWinningHandSplits(gamedata, 3, 4))