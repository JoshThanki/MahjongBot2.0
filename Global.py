import json
import os
import random
import time
import traceback
import numpy as np
from numpy.typing import NDArray
from xml.dom import minidom
import xml.etree.ElementTree as ET

import bz2
import sqlite3
from lxml import etree
from tqdm import tqdm


import copy

# converts hand from xml format
def format_xmlHand(string):
    if string == '':
        return [0]*34

    out=np.zeros(34, dtype=int)
    string_list = string.split(",")
    array = np.array([int(i) for i in string_list])
    for i in array:
        out[i // 4] +=1
    return out


# Calculates shanten number for a given hand
# input: hand array of length 34
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


#prints a matrix in readable format
def matprint(mat, fmt="g", file = None):
    col_maxes = [max([len(("{:"+fmt+"}").format(x)) for x in col]) for col in mat.T]
    for x in mat:
        for i, y in enumerate(x):
            print(("{:"+str(col_maxes[i])+fmt+"}").format(y), end="  " , file=file)
        print("" , file=file )


windDict = {
        0 : "E",
        1 : "S",
        2: "W",
        3 : "N"
    }


tile_dic = {i: f"{i+1}m" if i <= 8 else f"{i-8}p" if i <= 17 else f"{i-17}s" for i in range(27)}
honour_entries = {27 : "e", 28 : "s", 29 : "w", 30 : "n", 31 : "wd", 32 : "gd", 33 : "rd", -128:"None"}
tile_dic.update(honour_entries)




# formats hand into web format (can be plugged into: https://tenhou.net/2/?q=4566788m456p2246s)
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


# prints gameState matrix into a readable format for debugging
def printNice(game, file = None):
    int_game = [[int(element) for element in row] for row in game]
    game=int_game
    print("round wind: ", game[0][0], "| dealer: ", game[0][1], "| tilesInWall: ", game[0][5], "| doras: ", webFormat(game[1]), "| roundNum: ", game[0][33], "| honba sticks: ", game[0][3], "| riichi sticks: ", game[0][4],"| scores", game[0][6:10] , file=file )
    print("POV wind: "+ windDict[ game[0][2] ]+ " | POVHand: ", webFormat(game[2]) , file=file )  

    for i in range(4):
        print("player"+str(i)+ "| #chi=", game[0][14+i], "| #pon=", game[0][18+i], "| #kan=", game[0][22+i], "| #isOpen=", game[0][26+i],"| #isRiichi=", game[0][10+i],"| melds: "+webFormat(game[3+i]) , file=file )
    for i in range(4):
        print("player"+str(i)+" pool: ",webFormat(game[7+i]) , file=file)


# decodes meld (from integer)
def decodeMeld(data): #chi:0, pon:1, kan: 2, chakan:3
    def decodeChi(data):
        meldType = 0
        t0, t1, t2 = (data >> 3) & 0x3, (data >> 5) & 0x3, (data >> 7) & 0x3
        baseAndCalled = data >> 10
        called = baseAndCalled % 3
        base = baseAndCalled // 3
        base = (base // 7) * 9 + base % 7
        tiles = [(t0 + 4 * (base + 0))//4, (t1 + 4 * (base + 1))//4, (t2 + 4 * (base + 2))//4]
        return tiles, meldType

    def decodePon(data):
        t4 = (data >> 5) & 0x3
        t0, t1, t2 = ((1,2,3),(0,2,3),(0,1,3),(0,1,2))[t4]
        baseAndCalled = data >> 9
        called = baseAndCalled % 3
        base = baseAndCalled // 3
        if data & 0x8:
            meldType = 1
            tiles = [(t0 + 4 * base)//4, (t1 + 4 * base)//4, (t2 + 4 * base)//4]
        else:
            meldType = 3
            tiles = [(t0 + 4 * base)//4, (t1 + 4 * base)//4, (t2 + 4 * base)//4]
        return tiles, meldType

    def decodeKan(data, fromPlayer):
        baseAndCalled = data >> 8
        if fromPlayer:
            called = baseAndCalled % 4
        base = baseAndCalled // 4
        meldType = 2
        tiles = [base, base, base, base]
        return tiles, meldType

    data = int(data)
    meld = data & 0x3
    if data & 0x4:
        meld = decodeChi(data)
    elif data & 0x18:
        meld = decodePon(data)
    else:
        meld = decodeKan(data, False)
    return meld




