import numpy as np
import copy

from itertools import combinations

def taatsu(hand):
    sides = [[tile,tile+1] for tile in range(26) if (hand[tile] and hand[tile+1] and (tile%9 <= 7))]

    edges = [[tile,tile+2] for tile in range(25) if (hand[tile] and hand[tile+2] and (tile%9 <= 6))]

    return sides + edges

def pairs(hand):
    possiblePairs=[[tile]*2 for tile in range(34) if hand[tile]>=2]

    return possiblePairs


def checkPair(tatArr):
    out = False
    for i in tatArr:
        if i[0]==i[1]: out = True
    return out


def findTaatsu(hand):
    best_combination_tat = []
    maxTaatsuNum = 0
    maxPairPresence = False

    taatsuArr = taatsu(hand)
    pairArr = pairs(hand)
    
    arr = taatsuArr+pairArr
    print(arr)
    n = len(arr)

    for r in reversed(range(n+1)):
        if maxTaatsuNum: 
            break

        for combination in combinations(arr, r):
            if not combination: 
                continue

            out = np.zeros(34, dtype=int)
            for tat in combination:
                for tile in tat:
                    out[tile]+=1

            if np.all(out <= hand):
                best_combination_tat.append(list(combination))
                maxTaatsuNum = r

        return best_combination_tat#



def findWinningHandSplits(hand, numOpen):
    best_combination = []
    groups = getGroups(hand)
    print(groups)

    GroupsToFind = 4 - numOpen

    for combination in combinations(groups, GroupsToFind):

        out = np.zeros(34, dtype=int)
        for group in combination:
            for tile in group:
                out[tile]+=1

        if np.all(out <= hand) and np.isin(2, hand-out):
            best_combination.append(list(combination)+ [(hand-out).tolist().index(2)])

    
    return best_combination



def getGroups(hand):
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

    return manTriplets+manSequences+ pinTriplets+pinSequences+ souTriplets+souSequences+ honourTriplets


def calcShanten(hand):
    best_combination = []
    best_combination_tat = []
    maxGroupNum = 0

    groups = triplets(hand)

    shan = 128

    for r in [4,3,2,1]:
        if maxGroupNum: 
            break

        for combination in combinations(groups, r):

            out = np.zeros(34, dtype=int)
            for group in combination:
                for tile in group:
                    out[tile]+=1


            if np.all(out <= hand) and bestTaatsu(hand-out, r)<shan:
                shan = bestTaatsu(hand-out, r)
                


    
    return shan

def webFormat(handArray):
    dict = {0: 'm',
        1: 'p',
        2: 's',
        3: 'z'         #note the ordering here: manzu, pinzu, souzu (same as paper)
    }
    split_indices=[9,18,27]
    handArray =  np.split(handArray, split_indices) 
    string = ''

    for k, suit in enumerate(handArray):
        if sum(suit) == 0:
            continue
        for num in range(len(suit)):
            if suit[num] == 0:  continue
            else:  string += str(num+1)*suit[num]
        
        string += dict[k]

    return string






hand = [0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 3, 0]
hand = [0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0]
print(webFormat(hand))
print(findWinningHandSplits(hand, 0))




