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

import sqlite3

import copy

dbfile = 'es4p.db'

con = sqlite3.connect(dbfile)

cur = con.cursor()

res = cur.execute(f"SELECT log_id, log_content FROM logs")

#redefine numGames so don't cook my computer
NUMGAMES = 200

logs = []
for i in range(NUMGAMES):
    logs.append(res.fetchone())

con.close()




#global functions
def calcShanten(hand):
    
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
    
    def complete_sequences(suit_arr):
        possible_sequences=[]
        for i in range(2,9):
            if suit_arr[i]>0 and suit_arr[i-1]>0 and suit_arr[i-2]>0:
                out = [0]*9
                out[i]=1
                out[i-1]=1
                out[i-2]=1
                possible_sequences.append(out)
        return possible_sequences
    
    def incomplete_sequences(suit_arr):
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
    
    def resulting_hand(arr1,arr2):
        out=[0]*9
        for i in range(9):
            out[i] = arr1[i] - arr2[i]
        return out
    
    def splits_nogroups(hand):
        set_insequences = incomplete_sequences(hand)
        current_shan=0
        set_pairs = pairs(hand)
        pair_bool = False

        for i in set_pairs:
            current = splits_nogroups(resulting_hand(hand, i))[0]+1
            if current>current_shan:
                current_shan = current
                pair_bool = True

        for i in set_insequences:
            current = splits_nogroups(resulting_hand(hand, i))[0]+1
            if current > current_shan:
                current_shan = current
                pair_bool = splits_nogroups(resulting_hand(hand, i))[1]

        return current_shan, pair_bool

    def splits(g, hand):                  #******
        current_g_n = g                   #number of groups
        current_i_n = 0                   #number of taatsu
        pair_presance = False             #used for an edge case(s?)                            
        set_seq = complete_sequences(hand)
        set_triplets = triplets(hand)

        for j in set_seq:
            current_split = splits(g+1, resulting_hand(hand,j))   
            current = current_split[0]
            if current>current_g_n:
                current_g_n = current
                current_i_n = current_split[1]
                pair_presance = current_split[2]   #*
            elif current == current_g_n:
                if current_split[1] > current_i_n:
                    current_i_n = current_split[1]
                    pair_presance = current_split[2]   #*

        for j in set_triplets:
            current_split = splits(g+1, resulting_hand(hand,j))
            current = current_split[0]
            if current>current_g_n:
                current_g_n = current
                current_i_n = current_split[1]
                pair_presance = current_split[2]   #*
            elif current == current_g_n:
                if current_split[1] > current_i_n:
                    current_i_n = current_split[1]
                    pair_presance = current_split[2]   #*
 
        if (not set_seq) and (not set_triplets):     #if no more groups then counts maximum of taatsu    
            s=splits_nogroups(hand)
            return g, s[0], s[1]

        return current_g_n,current_i_n,pair_presance

    def splits_fullhand(hand):
        current_split = [0,0,False]
        for i in hand[:3]:
            current_arr = splits(0, i)
            current_split[0] += current_arr[0]
            current_split[1] += current_arr[1]
            if current_arr[2] == True:
                current_split[2] = True
        for i in hand[3]:
            if i == 3:
                current_split[0] += 1
            elif i == 2:
                current_split[1] +=1
                current_split[2] = True
        return current_split

    def general_shanten(handArray):
        split_arr = splits_fullhand(handArray)
        i = split_arr[1]
        g = split_arr[0]
        pair_presence = split_arr[2]
        p=0

        #checking for the edge cases:
        if i >= 5-g and pair_presence == False:
            p=1
        return 8 - 2*g - min(i, 4-g) - min(1, max(0,i+g-4)) + p
    def chiitoistu_shanten(handArray):
        pairs = 0
        for suit in handArray:
            for num in suit:
                pairs += num//2      #counts number of pairs, 4 of the same tile are treated as 2 pairs
        return 6 - pairs

    def orphanSource_shanten(handArray):
        diffTerminals = 0
        pairsTerminals = 0
        pair_const = 0
        for i in (0,8):                  #iterates over numbered suits
            for suit in handArray[:3]:
                pairsTerminals += min(1, suit[i]//2)
                diffTerminals += min(1, suit[i]//1)
        for num in handArray[3]:        #iterates over honours
                pairsTerminals += min(1, num//2)
                diffTerminals += min(1, num//1)
        if pairsTerminals > 0:
            pair_const=1
        return 13 - diffTerminals - pair_const

    return min(general_shanten(handArray), chiitoistu_shanten(handArray), orphanSource_shanten(handArray))


def format_xmlHand(string):
    if string == '':
        return [0]*34

    out=np.zeros(34, dtype=int)
    string_list = string.split(",")
    array = np.array([int(i) for i in string_list])
    for i in array:
        out[i // 4] +=1
    return out


def matprint(mat, fmt="g", file = None):
    col_maxes = [max([len(("{:"+fmt+"}").format(x)) for x in col]) for col in mat.T]
    for x in mat:
        for i, y in enumerate(x):
            print(("{:"+str(col_maxes[i])+fmt+"}").format(y), end="  " , file=file)
        print("" , file=file )

    # returns tiles, meldType



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

windDict = {
        0 : "E",
        1 : "S",
        2: "W",
        3 : "N"
    }

# formatting hand into web format from mahjong 1.0
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
            if suit[num] == 0:
                continue
            else:
                string += str(num+1)*suit[num]

        string += dict[k]

    return string


class Matrix:     
    def __init__(self):
        self.gameState = np.zeros((11, 34))
        self.privateHands = [[0]*34 , [0]*34 , [0]*34 , [0]*34]
        self.playerMelds = [[0]*34 , [0]*34 , [0]*34 , [0]*34]
        self.playerPool = [[0]*34 , [0]*34 , [0]*34 , [0]*34]
        self.doras = [0]*34
        self.notRiichi = [True, True, True, True]

        # metadata
        self.roundWind = 0   #0:E, 1:S, ...
        self.playerScores = [0, 0, 0, 0]
        self.playerWinds = [0,1,2,3]
        self.honbaSticks = 0
        self.roundWind = 0
        self.roundDealer = 0
        self.wallTiles = 70      # technically 69 but the dataset considers dealer 14th tile as a draw
        self.chisNum = [0,0,0,0]    #
        self.ponsNum = [0,0,0,0]    # num of melds for each player
        self.kansNum = [0,0,0,0]    #

        #used to keep track of things
        self.lastDrawPlayer = 0
        self.lastDrawTile = 0       
        self.lastDiscardPlayer = 0
        self.lastDiscardTile = 0
        self.closedKans = [0,0,0,0]       
        self.Closed = [True, True, True, True]  
        self.playerPons = [[], [], [], []]        #pons for each player, need for closed kan/chankan 

    def getnotRiichi(self, player):   #needed
        return self.notRiichi[player]
    
    def setRiichi(self, player):
        self.notRiichi[player] = False

    # builds matrix for POV player
    # forMeld   Riichi: False , Meld: true   (only difference is last discard)   
    def buildMatrix(self, player, forOpenCall):
        # player ordering relative to input player. e.g. player =2  => player_ordering = [2,3,0,1]   (counterclockwise on table)
        player_ordering = [i%4 for i in range(player,player+4)]

        #round wind
        self.gameState[0][0] = self.roundWind
        #dealer
        self.gameState[0][1] = player_ordering.index(self.roundDealer)
        #pov wind
        self.gameState[0][2] = self.playerWinds[player]        
        #num of honba sticks
        self.gameState[0][3] = self.honbaSticks
        #num of riichi sticks
        self.gameState[0][4] = self.notRiichi.count(False)  
        #num of tiles left in wall (kans might mess this up need to check)
        self.gameState[0][5] = self.wallTiles
        #padding
        self.gameState[0][30:33] = -128
        #round number
        self.gameState[0][33] = self.roundDealer + 1    
        
        #pov hand
        self.gameState[2] = self.privateHands[player]

        for index,player in enumerate(player_ordering):
            #melds
            self.gameState[3+index] = self.playerMelds[player]
            #pools
            self.gameState[7+index] = self.playerPool[player]

            #scores
            self.gameState[0][6+index] = self.playerScores[player]
            #riichis
            self.gameState[0][10+index] = 0 if self.notRiichi[player] else 1 
            #number of chis
            self.gameState[0][14+index] = self.chisNum[player]
            #number of pons
            self.gameState[0][18+index] = self.ponsNum[player]
            #number of kans
            self.gameState[0][22+index] = self.kansNum[player]
            # 0: closed, 1: open
            self.gameState[0][26+index] = 0 if self.Closed[player] else 1


        # sets last discard for the meld matrices
        if forOpenCall:
            self.gameState[0][30] = self.lastDiscardTile


    

    def getMatrix(self):  
        return self.gameState
    
    def addPlayerPonTiles(self, player, tiles):
        self.playerPons[player].append(tiles[0])

    def decPlayerPonTiles(self, player, tiles):
        self.playerPons[player].remove(tiles[0])

    def getPlayerPonTiles(self, player):
        return self.playerPons[player]

    def addClosedKan(self, player):
        self.closedKans[player] += 1           

    def getClosedKan(self, player):  #needed
        return self.closedKans[player]

    def addPlayerPool(self, player, tile):
        self.playerPool[player][tile] += 1

    def decPlayerPool(self, player, tile):
        self.playerPool[player][tile] -= 1
    
    def addChi(self, player):
        self.chisNum[player] += 1

    def addPon(self, player):
        self.ponsNum[player] += 1

    def decPon(self, player):
        self.ponsNum[player] -= 1

    def addKan(self, player):
        self.kansNum[player] += 1

    def addMeldNum(self, player, meldType):
        if meldType == 0:
            self.addChi(player)
        elif meldType == 1:
            self.addPon(player)
        elif meldType == 2:
            self.addKan(player)    

    # initialises starting hands for each player
    def initialisePrivateHands(self, hands):
        for player in range(4):
            self.privateHands[player] = hands[player]

    #input player (0-3) tile (0-34)
    def addTilePrivateHand(self, player, tile):
        self.privateHands[player][tile] += 1

    #input player (0-3) tile (0-34)
    def removeTilePrivateHand(self, player, tile):
        self.privateHands[player][tile] -= 1

    def getPrivateHand(self, player):
        return self.privateHands[player]
    
    # this is dependant on roundDealer so should only be called once the dealer is set
    def setPlayerWinds(self):
        dealer = self.roundDealer
        self.playerWinds = np.roll(self.playerWinds, dealer)

    def setRoundWind(self, wind):
        self.roundWind = wind
    
    def setDealer(self, dealer):
        self.roundDealer = dealer

    #input amount 
    def setHonbaSticks(self, amount):
        self.honbaSticks = amount
    
    #decrement wall tiles by one
    def decWallTiles(self):
        self.wallTiles -=1
    
    def getWallTiles(self):
        return self.wallTiles
    
    def setPlayerScore(self, scores):
        self.playerScores = scores
    
    def getPlayerScore(self, player):
        if player in [0,1,2,3]:
            return self.playerScores[player]
        else:
            print("Invalid Player")
    
    def setLastDiscardPlayer(self, player):
        self.lastDiscardPlayer = player

    def getLastDiscardPlayer(self):
        return self.lastDiscardPlayer

    def setLastDiscardTile(self, tile):
        self.lastDiscardTile = tile

    def getLastDiscardTile(self):
        return self.lastDiscardTile
    
    def setLastDrawPlayer(self, player):
        self.lastDrawPlayer = player

    def getLastDrawPlayer(self):
        return self.lastDrawPlayer
    
    def setLastDrawTile(self, tile):
        self.lastDrawTile = tile

    def getLastDrawTile(self):
        return self.lastDrawTile

    #input tile (0-34)
    def addDoraIndicator(self, doraIndicator):
        self.gameState[1][doraIndicator] += 1
            
    def canPon(self, player, tile):
        return (self.privateHands[player][tile] >= 2)

    def canKan(self, player, tile):
        return (self.privateHands[player][tile] == 3)

    def canChi(self, player, tile): # need to write logic to check for seat (can only chi from person before you)
        if tile//9 == 3: return False
        else:
            t = tile % 9
            h = self.privateHands[player]
            # skull
            if t == 0: return (h[tile+1]>0 and h[tile+2]>0)
            elif t == 8: return (h[tile-1]>0 and h[tile-2]>0)
            elif t == 1: return (h[tile+1]>0 and h[tile+2]>0) or (h[tile-1]>0 and h[tile+1]>0)
            elif t == 7: return (h[tile-1]>0 and h[tile-2]>0) or (h[tile-1]>0 and h[tile+1]>0)
            else: return (h[tile-1]>0 and h[tile-2]>0) or (h[tile-1]>0 and h[tile+1]>0) or (h[tile+1]>0 and h[tile+2]>0)
    
    def setOpen(self, player):
        self.Closed[player] = False
    
    def getClosed(self, player):
        return self.Closed[player]

    def handleDraw(self, player, tile):
        self.setLastDrawPlayer(player)   
        self.setLastDrawTile(tile)
        self.decWallTiles()                   # remove a wall tile after drawing
        self.addTilePrivateHand(player, tile)      # add the drawn tile to hand

    def handleDiscard(self, player, tile):
        self.setLastDiscardPlayer(player)
        self.removeTilePrivateHand(player, tile)   # remove discarded tile from hand 
        self.setLastDiscardTile(tile)

    def initialiseGame(self, data):
        #sets points
        points = [int(i) for i in data["ten"].split(",")]
        self.setPlayerScore(points)
        
        #sets player winds
        self.setDealer(int(data["oya"]))
        self.setPlayerWinds()

        #sets starting hands
        initialHands = [format_xmlHand(data["hai"+str(i)]) for i in range(4) ]
        self.initialisePrivateHands(initialHands)

        #sets more metadata form seed
        seed = [int(i) for i in data["seed"].split(',')]
        self.addDoraIndicator(seed[5] // 4)
        self.setHonbaSticks(seed[1])
        self.setRoundWind(seed[0] //4)
        self.setDealer(seed[0] % 4)


    def handleMeld(self, player, meldInfo, isClosedKan):
        meldTiles = meldInfo[0]
        meldType = meldInfo[1]

        # handles closed kan
        if isClosedKan:
            self.privateHands[player][ meldTiles[0] ] = 0
            self.addKan(player)
            self.playerMelds[player][ meldTiles[0] ] = 4
            
        # handles chakan
        elif meldType == 3: 
            self.decPlayerPonTiles(player, meldTiles)
            self.decPon(player)
            self.playerMelds[player][ meldTiles[0] ] = 4
            self.addKan(player)
            self.privateHands[player][ meldTiles[0] ] = 0

        # handles regular call
        else:
            self.setOpen(player)
            # adds meld tiles to meld attribute
            for tile in meldTiles:
                self.playerMelds[player][tile] += 1 

            called = self.lastDiscardTile
            meldTiles.remove(called)  
            #removes tiles from player hand
            for tile in meldTiles:
                self.privateHands[player][tile] -= 1
            # adds pon if pon
            if meldType == 1:
                self.addPlayerPonTiles(player, meldTiles)
            # adds meld number
            self.addMeldNum(player, meldType)


drawDic = {
    'T': 0,
    'U': 1,
    'V': 2,
    'W': 3
}

discardDic = {
    'D': 0,
    'E': 1,
    'F': 2,
    'G': 3
}

def matrixifymelds(arr):

    chiArr = []
    ponArr = []
    kanArr = []

    def handleMeldsOtherPlayers():
        discardPlayer = matrix.getLastDiscardPlayer()
        tile = matrix.getLastDiscardTile()
        
        players = [0,1,2,3]
        players.remove(discardPlayer)  # discard player cant call the tile

        for player in players:
            isNextCallChi, isNextCallPon, isNextCallKan = False, False, False,
            chiLabel, ponLabel, kanLabel = 0, 0, 0

            previousPlayer = (player+3)%4
            isValidChiPlayer =  (discardPlayer == previousPlayer)
            isCurrentPlayer_NotInRiichi = matrix.getnotRiichi(player)

            nextMove  = arr[index+1]
            isNextMoveCall = (nextMove[0] == "N")

            if isNextMoveCall:
                meldType = decodeMeld( int(nextMove[1]["m"]) )[1]
                isCurrentPlayerCallPlayer = (int(nextMove[1]["who"])==player)
                isNextCallChi = (meldType==0)
                isNextCallPon = (meldType==1)
                isNextCallKan = (meldType==2)

    
            ### CHI ###
            if isValidChiPlayer and matrix.canChi(player, tile) and isCurrentPlayer_NotInRiichi:
                matrix.buildMatrix(player, True)
                # if the player calls the tile and the call is chi
                if isNextCallChi and isCurrentPlayerCallPlayer: 
                    chiLabel = 1
                    # removes the tile from the wall since it got called
                    matrix.decPlayerPool(discardPlayer, tile)

                chiArr.append([copy.deepcopy(matrix.getMatrix()), chiLabel])

            ### PON ### 
            if matrix.canPon(player, tile) and isCurrentPlayer_NotInRiichi:
                matrix.buildMatrix(player, True)
                if isNextCallPon and isCurrentPlayerCallPlayer: 
                    ponLabel = 1
                    matrix.decPlayerPool(discardPlayer, tile)
                ponArr.append([copy.deepcopy(matrix.getMatrix()), ponLabel])

            ### KAN ###
            if matrix.canKan(player, tile) and isCurrentPlayer_NotInRiichi:
                matrix.buildMatrix(player, True)
                if isNextCallKan and isCurrentPlayerCallPlayer: 
                    kanLabel = 1
                    matrix.decPlayerPool(discardPlayer, tile)
                kanArr.append([copy.deepcopy(matrix.getMatrix()), kanLabel])


    def handleMeldsSelf():
        drawPlayer = matrix.getLastDrawPlayer()   
        drawTile = matrix.getLastDrawTile()  
        hand = matrix.getPrivateHand(drawPlayer)

        isNextMoveCall = (arr[index+1][0] == "N")

        closedKanLabel, chankanLabel = 0, 0

        ### CLOSED KAN ###
        # If the player has 4 of the same tile then builds the matrix and appends it with the label to kanArr
        for tile in range(34):
            if hand[tile] == 4:
                matrix.buildMatrix(drawPlayer, True)
                if isNextMoveCall:
                    closedKanLabel = 1
                kanArr.append([copy.deepcopy(matrix.getMatrix()), closedKanLabel])
                break
                ##### perhaps have lastDiscard = lastDraw in this,  altough that would cause issues

        ### CHANKAN ###
        for tile in range(34):
            playerHasTile_inHand = (hand[tile]>0)
            playerHasTile_inPon = (tile in matrix.getPlayerPonTiles(drawPlayer))

            if playerHasTile_inHand and playerHasTile_inPon:
                matrix.buildMatrix(drawPlayer, True)
                if isNextMoveCall:
                    chankanLabel = 1
                kanArr.append([copy.deepcopy(matrix.getMatrix()), chankanLabel])
                break


    for index,item in enumerate(arr): 
        if item[1]:
            attr = item[1]

            if item[0] == "INIT":
                #clears matrix attributes
                matrix = Matrix() 
                #initializes start of game
                matrix.initialiseGame(attr)

            elif item[0] == "N":
                meldInfo = decodeMeld(attr["m"])
                player = int( attr["who"] )
                isClosedKan = (player == matrix.getLastDrawPlayer()) and arr[index-2][0] != "N"

                matrix.handleMeld(player, meldInfo, isClosedKan)
          
            elif item[0] == "DORA":
                matrix.addDoraIndicator( int(attr["hai"]) // 4 )
            
            elif item[0] == "REACH":
                matrix.setRiichi( matrix.getLastDrawPlayer() )
                if attr["step"] == "2":
                    points = [int(i) for i in attr["ten"].split(",")]
                    matrix.setPlayerScore(points) 

        else:
            attr = item[0]        # attr in the form of, say, T46
            moveIndex = attr[0]   # T
            tile = int(attr[1:]) // 4  # 46 // 4

            #### DRAWS ####
            if moveIndex in drawDic:
                curPlayer = drawDic[moveIndex]
                matrix.handleDraw(curPlayer, tile)
                handleMeldsSelf()    

            #### DISCARDS ####  
            else:
                curPlayer = discardDic[moveIndex]
                matrix.handleDiscard(curPlayer, tile)
                matrix.addPlayerPool(curPlayer, tile)  # Always adds pool in this function and if the tile gets called then it deletes it from pool
                handleMeldsOtherPlayers()
                
    return chiArr, ponArr, kanArr


def matrixify(arr):
    reachArr = []

    #riichi conditions are: the player is not already in riichi, hand is closed, is in tenpai, and >=4 tiles in live wall (rule)
    #checks for riichi conditions, and then appends to reachArr if passes necessary conditions
    def handleRiichi(p):
        hand = matrix.getPrivateHand(p)
        if matrix.getnotRiichi(p) and matrix.getClosed(p) and (calcShanten(hand) <= 2*matrix.getClosedKan(p)) and matrix.getWallTiles() >= 4:
            riichiLabel = 0
            matrix.buildMatrix(p, False)
            # if riichis then sets to riichi
            if arr[index+1][0] == "REACH": 
                riichiLabel = 1
                matrix.setRiichi(p)
            reachArr.append([copy.deepcopy(matrix.getMatrix()), riichiLabel]) 

    for index,item in enumerate(arr): 
        if item[1]:
            attr = item[1]

            if item[0] == "INIT":
                #clears matrix attributes
                matrix = Matrix() 
                #initializes start of game 
                matrix.initialiseGame(attr)

            elif item[0] == "N":
                meldInfo = decodeMeld(attr["m"])
                player = int( attr["who"] )
                isClosedKan = (player == matrix.getLastDrawPlayer()) and arr[index-2][0] != "N"
                
                matrix.handleMeld(player, meldInfo, isClosedKan)
 
            # if new dora then adds it
            elif item[0] == "DORA":
                matrix.addDoraIndicator( int(attr["hai"]) // 4 )

            elif (item[0] == "REACH") and attr["step"] == "2":
                points = [int(i) for i in attr["ten"].split(",")]
                matrix.setPlayerScore(points) 


        else:
            attr = item[0]             # attr in the form of, say, T46
            moveIndex = attr[0]        # T
            tile = int(attr[1:]) // 4  # 46 // 4
            
            #### DRAWS ####
            if moveIndex in drawDic:
                curPlayer = drawDic[moveIndex]
                matrix.handleDraw(curPlayer, tile)
                handleRiichi(curPlayer)

            #### DISCARDS ####  
            else:
                curPlayer = discardDic[moveIndex]
                matrix.handleDiscard(curPlayer, tile)
                if arr[index+1][0] != "N":
                    matrix.addPlayerPool(curPlayer, tile)

    return reachArr

def convertLog(log):

    game = log[0]

    blob = log[1]

    XML = etree.XML

    decompress = bz2.decompress

    content = decompress(blob)

    xml = XML(content, etree.XMLParser(recover=True))

    rough_string = ET.tostring(xml, encoding='unicode')

    root = ET.fromstring(rough_string)

    arr = []

    for element in root:

        header_name = element.tag
        
        attributes_dict = element.attrib

        arr.append((header_name ,  attributes_dict))

    return game, arr


out = [convertLog(logs) for logs in logs]



def printNice(game, file = None):
    int_game = [[int(element) for element in row] for row in game]
    game=int_game
    print("round wind: ", game[0][0], "| dealer: ", game[0][1], "| tilesInWall: ", game[0][5], "| doras: ", webFormat(game[1]), "| roundNum: ", game[0][33], "| honba sticks: ", game[0][3], "| riichi sticks: ", game[0][4],"| scores", game[0][6:10] , file=file )
    print("POV wind: "+ windDict[ game[0][2] ]+ " | POVHand: ", webFormat(game[2]) , file=file )  

    for i in range(4):
        print("player"+str(i)+ "| #chi=", game[0][14+i], "| #pon=", game[0][18+i], "| #kan=", game[0][22+i], "| #isOpen=", game[0][26+i],"| melds: "+webFormat(game[3+i]) , file=file )
    for i in range(4):
        print("player"+str(i)+" pool: ",webFormat(game[7+i]) , file=file)


def manualTest(gameNum):
    tupl = out[gameNum]
    game = tupl[1]

    game_riichi = matrixify(game)
    game_chi = matrixifymelds(game)[0]
    game_pon = matrixifymelds(game)[1]
    game_kan = matrixifymelds(game)[2]

    print("gameid: ", tupl[0])
    for i in game_kan:
        mat=i[0]
        printNice(mat)
        print("label: ", i[1])
        print("last discard:", mat[0][30])
        matprint(i[0])
        print("")


#takes in game number from (0 - 200)

tile_dic = {i: f"{i+1}m" if i <= 8 else f"{i-8}p" if i <= 17 else f"{i-17}s" for i in range(27)}
honour_entries = {27 : "e", 28 : "s", 29 : "w", 30 : "n", 31 : "wd", 32 : "gd", 33 : "rd", -128:"None"}
tile_dic.update(honour_entries)

def printStates(states, file = None):
    for i in states:
            mat=i[0]
            printNice(mat, file=file)
            print("label: ", i[1] , file=file )
            print("call tile:", tile_dic[int(mat[0][30])] , file=file)
            #matprint(i[0], file=file)
            print("", file=file)


def printTestToFile(gameNum):

    with open("out.txt" , "w+") as file:

        tupl = out[gameNum]
        game = tupl[1]

        game_riichi = matrixify(game)
        game_chi = matrixifymelds(game)[0]
        game_pon = matrixifymelds(game)[1]
        game_kan = matrixifymelds(game)[2]


        print("gameid: ", tupl[0], file=file,)

        print("" , file=file )
        print("" , file=file)
        print("Riichi States" , file=file )
        printStates(game_riichi, file=file)

        print("" , file=file)
        print("" , file=file) 
        print("Chi States" , file=file)
        printStates(game_chi, file=file)

        print("" , file=file)
        print("" , file=file)
        print("Pon States" , file=file )
        printStates(game_pon, file=file)

        print("" , file=file)
        print("" , file=file)
        print("Kan States" , file=file)
        printStates(game_kan, file=file)




#statetype (0-4) 0 - riichi, 1 - chi, 2 - pon, 3- kan
def flatformat(states, logid, statetype, year):
    arr = []
    for i in states:
        mat = i[0]
        label = i[1]
        flat = mat.flatten()
        flat = np.append(flat, label)
        arr.append(flat)
    
    arr_np = np.array(arr)
    
    directory = os.path.join(".", "Data", str(year))
    os.makedirs(directory, exist_ok=True)
    
    file_path = os.path.join(directory, f"{statetype}_{logid}.npz")
    
    # Save the array as a compressed .npz file
    np.savez_compressed(file_path, arr_np)
        



def saveToFile(log, year):

    tupl = convertLog(log)

    game = tupl[1]
    gameid = tupl[0]

    game_riichi = matrixify(game)
    game_chi = matrixifymelds(game)[0]
    game_pon = matrixifymelds(game)[1]
    game_kan = matrixifymelds(game)[2]

    flatformat(game_riichi, gameid, 0, year)
    flatformat(game_chi, gameid, 1 , year)
    flatformat(game_pon, gameid, 2 , year) 
    flatformat(game_kan, gameid, 3 , year)


def saveFilesPerYear(year):

    dbfile = 'es4p.db'

    con = sqlite3.connect(dbfile)

    cur = con.cursor()

    res = cur.execute(f"SELECT COUNT(*) FROM logs WHERE year = {year}")

    NUMGAMES = 50

    print(NUMGAMES)

    res = cur.execute(f"SELECT log_id, log_content FROM logs WHERE year = {year}")

    #redefine games so it doesn't pull all of them 
    #DO NOT COMMENT UNLESS YOU WANT TO DOWNLOAD EVERYTHING
    NUMGAMES = 50
    
    for i in range(NUMGAMES):
        log = res.fetchone()

        try:
            saveToFile(log, year)
        except Exception as e:
            pass
            # print(f"An error occurred with i={i}: {e}")
            # traceback.print_exc()

    con.close()

def saveAll():
    for year in range(2016, 2021):
        saveFilesPerYear(year)

for i in range(1):
    
    print(i)
    printTestToFile(19)
"""
start_time = time.time()

saveAll()

end_time = time.time()

duration = end_time - start_time

print(f"saveAll() took {duration:.4f} seconds")
"""