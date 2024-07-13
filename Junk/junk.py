import numpy as np
import copy

def calcShanten(hand, numCalledMelds=0):    
    #converting to mahjong 1.0 format
    split_indices=[9,18,27]
    handArray =  np.split(hand, split_indices) 

    def pairs(suit_arr):
        possible_pairs=[]

        for i in range(9):
            if suit_arr[i]>1:
                out = [0]*9
                out[i] = 2
                possible_pairs.append(out)
        return possible_pairs
    
    def triplets(suit_arr):
        possible_triplets=[]

        for i in range(9):
            if suit_arr[i]>2:
                out = [0]*9
                out[i] = 3
                possible_triplets.append(out)
        return possible_triplets
    
    def completeSequences(suit_arr):
        possible_sequences=[]
        for i in range(2,9):
            if suit_arr[i]>0 and suit_arr[i-1]>0 and suit_arr[i-2]>0:
                out = [0]*9
                out[i]=1
                out[i-1]=1
                out[i-2]=1
                possible_sequences.append(out)
        return possible_sequences
    
    def incompleteSequences(suit_arr):
        possible_insequences=[]
        if suit_arr[0]>0 and suit_arr[1]>0:
            out = [0]*9
            out[0]=1
            out[1]=1
            possible_insequences.append(out)
        for i in range(2,9):
            if suit_arr[i]>0 and suit_arr[i-1]>0:
                out = [0]*9
                out[i]=1
                out[i-1]=1
                possible_insequences.append(out)
            if suit_arr[i]>0 and suit_arr[i-2]>0:
                out = [0]*9
                out[i]=1
                out[i-2]=1
                possible_insequences.append(out)
        return possible_insequences
    

    def splitsNoGroups(hand):
        maxTaatsuNum = 0
        maxPairPresence = False

        setInseqs = incompleteSequences(hand)
        setPairs = pairs(hand)

        for pair in setPairs:
            currTaatsuNu = splitsNoGroups( hand - pair )[0] + 1
            if currTaatsuNu > maxTaatsuNum:
                maxTaatsuNum = currTaatsuNu
                maxPairPresence = True

        for inSeq in setInseqs:
            currTaatsuNum, currPairPresence = splitsNoGroups( hand - inSeq )
            currTaatsuNum += 1
            if currTaatsuNum > maxTaatsuNum:
                maxTaatsuNum = currTaatsuNum
                maxPairPresence = currPairPresence

        return maxTaatsuNum, maxPairPresence


    def splits(hand, groupNum=0, pair_presence=False):  
        maxGroupNum = groupNum                   #number of groups
        maxTaatsuNum = 0                          #number of taatsu           #used for an edge case(s?)                            
        maxPairPresence = pair_presence        
        
        setSeqs = completeSequences(hand)
        setTriplets = triplets(hand)

        for seq in setSeqs:
            currGroupNum, currTaatsuNum, currPairPresence  = splits( hand-seq, groupNum+1, pair_presence)   
            
            if currGroupNum > maxGroupNum:
                maxGroupNum = currGroupNum
                maxTaatsuNum = currTaatsuNum
                maxPairPresence = currPairPresence

            elif currGroupNum == maxGroupNum:
                if currTaatsuNum > maxTaatsuNum:
                    maxTaatsuNum = maxGroupNum
                    maxPairPresence = currPairPresence

                elif (currTaatsuNum == maxTaatsuNum) and (pair_presence):
                    maxTaatsuNum = currTaatsuNum
                    maxPairPresence = currPairPresence

        for triplet in setTriplets:
            currGroupNum, currTaatsuNum, currPairPresence  = splits( hand-triplet, groupNum+1, pair_presence)   
            if currGroupNum > maxGroupNum:
                maxGroupNum = currGroupNum
                maxTaatsuNum = currTaatsuNum
                maxPairPresence = currPairPresence

            elif currGroupNum == maxGroupNum:
                if currTaatsuNum > maxTaatsuNum:
                    maxTaatsuNum = maxGroupNum
                    maxPairPresence = currPairPresence
                
                elif (currTaatsuNum == maxTaatsuNum) and (pair_presence):
                    maxTaatsuNum = currTaatsuNum
                    maxPairPresence = currPairPresence
 
        if (not setSeqs) and (not setTriplets):     #if no more groups then counts maximum of taatsu    
            maxTaatsuNum, maxPairPresence = splitsNoGroups(hand)

        return maxGroupNum, maxTaatsuNum, maxPairPresence


    def splitsTotal(hand):
        totalSplit = [0,0,False]

        for suitTiles in hand[:3]:
            suitSplit = splits( hand=suitTiles )
            totalSplit[0] += suitSplit[0]
            totalSplit[1] += suitSplit[1]
            if suitSplit[2] == True:
                totalSplit[2] = True

        for honourTile in hand[3]:
            if honourTile == 3:
                totalSplit[0] += 1
            elif honourTile == 2:
                totalSplit[1] +=1
                totalSplit[2] = True

        return totalSplit


    def general_shanten(handArray):
        totalSplit = splitsTotal(handArray)
        tatNum = totalSplit[1]
        groupNum = totalSplit[0] + numCalledMelds
        pairPresence = totalSplit[2]
        p=0

        #checking for the edge cases:
        if (tatNum >= 5-groupNum) and (not pairPresence):
            p=1

        return 8 - 2*groupNum - min(tatNum, 4 - groupNum) - min(1, max(0, tatNum + groupNum - 4) ) + p


    def chiitoistu_shanten(handArray):
        numPairs = 0

        for suit in handArray:
            for tile in suit:
                
                numPairs += tile//2      #counts number of pairs, 4 of the same tile are treated as 2 pairs
        
        return 6 - numPairs


    def orphanSource_shanten(handArray):
        diffTerminals = 0
        pairsTerminals = 0
        pairConstant = 0

        for i in (0,8):                  #iterates over numbered suits
            for suit in handArray[:3]:
                pairsTerminals += min(1, suit[i]//2)
                diffTerminals += min(1, suit[i])

        for num in handArray[3]:        #iterates over honours
            pairsTerminals += min(1, num//2)
            diffTerminals += min(1, num//1)

        if pairsTerminals > 0:
            pairConstant=1

        return 13 - diffTerminals - pairConstant


    return min(general_shanten(handArray), chiitoistu_shanten(handArray), orphanSource_shanten(handArray))



def possibleChis(hand, tile):
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


def bestChi(hand, tile, meldNum):
    currenthand = hand

    resMeldNum = meldNum+1    

    minShanten = 128
    bestChiBase = None

    for chiBaseTile in possibleChis(hand, tile):
        curShanten = calcShanten(hand=handAfterChi(hand, chiBaseTile, tile),  numCalledMelds=resMeldNum)

        if curShanten < minShanten:
            minShanten = curShanten
            bestChiBase = chiBaseTile

    return bestChiBase

def handAfterChi(hand, chiBase, called):
    handCopy= copy.copy(hand)

    chiTiles = [chiBase,chiBase+1,chiBase+2]
    chiTiles.remove(called)

    for i in chiTiles:
        handCopy[i] -= 1

    return handCopy
        

#print(handAfterChi([1,1,0,0,0,0,0,0,0], 0,2))

hand = [0]*34
hand[:5]=[1,1,0,1,1]

print( possibleChis(hand, 2))
print( bestChi(hand, 2, 3)  )
