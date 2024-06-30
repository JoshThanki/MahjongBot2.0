import json
import random
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

dbfile = '2020.db'

con = sqlite3.connect(dbfile)

cur = con.cursor()

res = cur.execute("SELECT log_id, log_content FROM logs")

logs = []

for i in range(20):
    logs.append(res.fetchone())

con.close()

out = {}


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


def matprint(mat, fmt="g"):
    col_maxes = [max([len(("{:"+fmt+"}").format(x)) for x in col]) for col in mat.T]
    for x in mat:
        for i, y in enumerate(x):
            print(("{:"+str(col_maxes[i])+fmt+"}").format(y), end="  ")
        print("")

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
        self.chis = [0,0,0,0]    #
        self.pons = [0,0,0,0]    # num of melds for each player
        self.kans = [0,0,0,0]    #

        #used to keep track of things
        self.lastDrawPlayer = -1
        self.lastDiscardPlayer = -1
        self.lastDiscardTile = -1
        self.closedKans = [0,0,0,0]       
        self.Closed = [True, True, True, True]    
    def getnotRiichi(self, player):   #needed
        return self.notRiichi[player]
    
    def setRiichi(self, player):
        self.notRiichi[player] = False

    # builds matrix for POV player
    # forMeld   Riichi: False , Meld: true   (only difference is last discard)   
    def buildMatrix(self, player, forMeld):
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
            self.gameState[0][14+index] = self.chis[player]
            #number of pons
            self.gameState[0][18+index] = self.pons[player]
            #number of kans
            self.gameState[0][22+index] = self.kans[player]
            # 0: closed, 1: open
            self.gameState[0][26+index] = 0 if self.Closed[player] else 1


        # sets last discard for the meld matrices
        if forMeld:
            self.gameState[0][30] = self.lastDiscardTile
    

    def getMatrix(self):  #needed
        return self.gameState
    

    # hand [34]
    def addClosedKan(self, player):
        self.closedKans[player] += 1           
    def getClosedKan(self, player):  #needed
        return self.closedKans[player]

    def addPlayerPool(self, player, tile):
        self.playerPool[player][tile] += 1

    def decPlayerPool(self, player, tile):
        self.playerPool[player][tile] -= 1
    
    def addChi(self, player):
        self.chis[player] += 1

    def addPon(self, player):
        self.pons[player] += 1

    def addKan(self, player):
        self.kans[player] += 1

    def addMeldNum(self, player, meldType):
        if meldType == 0:
            self.addChi(player)
        elif meldType == 1:
            self.addPon(player)
        elif meldType == 2:
            self.addKan(player)    

    def getPlayerPool(self, player):
        return self.playerPool[player]

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

    def getPlayerWinds(self):
        return self.playerWinds

    #input - 0,1,2,3
    def setRoundWind(self, wind):
        self.roundWind = wind

    def getRoundWind(self):
        return self.roundWind
    
    def setDealer(self, dealer):
        self.roundDealer = dealer

    def getDealer(self):
        return self.roundDealer

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

    #input tile (0-34)
    def addDoraIndicator(self, doraIndicator):
        self.gameState[1][doraIndicator] += 1
    
    def getDoraIndicators(self):
        return (self.gameState[1])
    
    #input player (0-3), meldinfo(([3-4] , (0-3) 0: chi,  1: pon, 2: open kan, 3: closed kan

    def addPlayerMelds(self, player, meldinfo, isClosedKan):
        meldTiles = meldinfo[0]
        for tile in meldTiles:
            self.playerMelds[player][tile] += 1 

        if isClosedKan:
            tile = meldTiles[0]
            self.privateHands[player][tile] -= 4 
        else:
            called = self.lastDiscardTile
            meldTiles.remove(called)  
            for tile in meldTiles:
                self.privateHands[player][tile] -= 1
    
    def getPlayerMelds(self):
        return self.playerMelds

    


    #meld functions
    def canPon(self, player, tile):
        return (self.privateHands[player][tile] >= 2)

    def canKan(self, player, tile):
        return (self.privateHands[player][tile] >= 3)

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





def matrixifymelds(arr):

    chiArr = []
    ponArr = []
    kanArr = []

    def format_seed(string):
        return [int(i)//4 for i in string.split(",")]


    def checkMelds():
        discardPlayer = matrix.getLastDiscardPlayer()
        tile = matrix.getLastDiscardTile()
        
        players = [0,1,2,3]
        players.remove(discardPlayer)  # discard player cant call the tile

        for player in players:
            # resp. labels:   0 if doesn't call, 1 if does
            chiLabel, ponLabel, kanLabel = 0, 0, 0
            
            # used for chi
            previousPlayer = ((player - 1) if player else 3)

            ### CHI ###
            if discardPlayer == previousPlayer and matrix.canChi(player, tile):
                matrix.buildMatrix(player, True)
                # if the player calls the tile
                if arr[index+1][0] == "N" and int(arr[index+1][1]["who"]) == player: 
                    chiLabel = 1
                    # removes the tile from the wall since it got called
                    matrix.decPlayerPool(discardPlayer, tile)

                chiArr.append([copy.deepcopy(matrix.getMatrix()), chiLabel])

            ### PON ### 
            elif  matrix.canPon(player, tile):
                matrix.buildMatrix(player, True)
                if arr[index+1][0] == "N" and int(arr[index+1][1]["who"]) == player: 
                    ponLabel = 1
                    matrix.decPlayerPool(discardPlayer, tile)
                ponArr.append([copy.deepcopy(matrix.getMatrix()), ponLabel])

            ### KAN ###
            elif  matrix.canKan(player, tile):
                matrix.buildMatrix(player, True)
                if arr[index+1][0] == "N" and int(arr[index+1][1]["who"]) == player: 
                    kanLabel = 1
                    matrix.decPlayerPool(discardPlayer, tile)
                kanArr.append([copy.deepcopy(matrix.getMatrix()), kanLabel])


    for index,item in enumerate(arr): 
        if item[1]:
            attr = item[1]
            if item[0] == "INIT":
                #clears matrix attributes
                matrix = Matrix() 
                
                #sets points
                points = [int(i) for i in attr["ten"].split(",")]
                matrix.setPlayerScore(points)
                
                #sets player winds
                matrix.setDealer(int(attr["oya"]))
                matrix.setPlayerWinds()

                #sets starting hands
                initialHands = [format_xmlHand(attr["hai"+str(i)]) for i in range(4) ]
                matrix.initialisePrivateHands(initialHands)

                #sets more metadata form seed
                seed = [int(i) for i in attr["seed"].split(',')]
                matrix.addDoraIndicator(seed[5] // 4)
                matrix.setHonbaSticks(seed[1])
                matrix.setRoundWind(seed[0] //4)
                matrix.setDealer(seed[0] % 4)

            elif item[0] == "N":
                meldInfo = decodeMeld(attr["m"])
                player = int( attr["who"] )

                # if player who called the meld and player who drew last tile match then it is a closed kan
                if (player != matrix.getLastDrawPlayer() ):
                    matrix.setOpen(player)
                    matrix.addPlayerMelds(player, meldInfo, False) 

                # bug if i have else instead of this elif in a very specific case (see round 1)
                elif arr[index-2][0] != "N":
                    matrix.addPlayerMelds(player, meldInfo, True) 
                    matrix.addClosedKan(player)

                else: 
                    matrix.setOpen(player)
                    matrix.addPlayerMelds(player, meldInfo, False) 

                #chi:0, pon:1, openKan:2, closedKain:3, chakan:4
                matrix.addMeldNum(player, meldInfo[1])
          
            elif item[0] == "DORA":
                matrix.addDoraIndicator( int(attr["hai"]) // 4 )
            
            elif item[0] == "REACH":
                matrix.setRiichi( matrix.getLastDrawPlayer() )
                if attr["step"] == "2":
                    points = [int(i) for i in attr["ten"].split(",")]
                    matrix.setPlayerScore(points) 

        else:
            #### DRAWS ####
            attr = item[0]        # attr in the form of, say, T46
            moveIndex = attr[0]   # T
            tile = int(attr[1:]) // 4  # 46 // 4

            if moveIndex == "T":
                matrix.setLastDrawPlayer(0)   
                hand = matrix.getPrivateHand(0)
                matrix.decWallTiles()                   # remove a wall tile after drawing
                matrix.addTilePrivateHand(0, tile)      # add the drawn tile to hand

            elif moveIndex == "U":
                matrix.setLastDrawPlayer(1)                   
                hand = matrix.getPrivateHand(1)
                matrix.decWallTiles()             
                matrix.addTilePrivateHand(1, tile)
                
            elif moveIndex == "V":
                matrix.setLastDrawPlayer(2)   
                hand = matrix.getPrivateHand(2)
                matrix.decWallTiles()        
                matrix.addTilePrivateHand(2, tile) 
                
            elif moveIndex == "W":
                matrix.setLastDrawPlayer(3)   
                hand = matrix.getPrivateHand(3)
                matrix.decWallTiles()           
                matrix.addTilePrivateHand(3, tile)  
                
            #### DISCARDS #### 
            elif moveIndex == "D":
                matrix.setLastDiscardPlayer(0)
                matrix.removeTilePrivateHand(0, tile)   # remove discarded tile from hand 
                matrix.setLastDiscardTile(tile)
                matrix.addPlayerPool(0, tile)  # Always adds pool in this function and if the tile gets called then it deletes it from pool

                # this function checks for any valid meld calls, builds the matrix if neeeded and appends it to the output arrays
                checkMelds()

            elif moveIndex == "E":
                matrix.setLastDiscardPlayer(1)
                matrix.removeTilePrivateHand(1, tile)  
                matrix.setLastDiscardTile(tile)
                matrix.addPlayerPool(1, tile)
                
                checkMelds()

            elif moveIndex == "F":
                matrix.setLastDiscardPlayer(2)
                matrix.removeTilePrivateHand(2, tile) 
                matrix.setLastDiscardTile(tile)
                matrix.addPlayerPool(2, tile)
                
                checkMelds()

            elif moveIndex == "G":
                matrix.setLastDiscardPlayer(3)
                matrix.removeTilePrivateHand(3, tile)
                matrix.setLastDiscardTile(tile)
                matrix.addPlayerPool(3, tile)
                
                checkMelds()
                
    return chiArr, ponArr, kanArr



def matrixify(arr):
    reachArr = []

    #riichi conditions are: the player is not already in riichi, hand is closed, is in tenpai, and >=4 tiles in live wall (rule)
    #checks for riichi conditions, and then appends to reachArr if passes necessary conditions
    def checkRiichi(p):
        hand = matrix.getPrivateHand(p)
        if matrix.getnotRiichi(p) and matrix.getClosed(p) and (calcShanten(hand) <= 2*matrix.getClosedKan(p)) and matrix.getWallTiles() >= 4:
            matrix.buildMatrix(p, False)
            # if riichis then sets to riichi
            if arr[index+1][0] == "REACH": 
                matrix.setRiichi(p)
            reachArr.append([copy.deepcopy(matrix.getMatrix()), 0 if matrix.getnotRiichi(p) else 1]) 

    for index,item in enumerate(arr): 
        if item[1]:
            attr = item[1]
            if item[0] == "INIT":
                #clears matrix attributes
                matrix = Matrix() 
                
                #sets points
                points = [int(i) for i in attr["ten"].split(",")]
                matrix.setPlayerScore(points)
                
                #sets player winds
                matrix.setDealer(int(attr["oya"]))
                matrix.setPlayerWinds()

                #sets starting hands
                initialHands = [format_xmlHand(attr["hai"+str(i)]) for i in range(4) ]
                matrix.initialisePrivateHands(initialHands)

                #sets more metadata form seed
                seed = [int(i) for i in attr["seed"].split(',')]
                matrix.addDoraIndicator(seed[5] // 4)
                matrix.setHonbaSticks(seed[1])
                matrix.setRoundWind(seed[0] //4)
                matrix.setDealer(seed[0] % 4) 

            elif item[0] == "N":
                meldInfo = decodeMeld(attr["m"])
                player = int( attr["who"] )

                # if player who called the meld and player who drew last tile match then it is a closed kan
                if (player != matrix.getLastDrawPlayer() ):
                    matrix.setOpen(player)
                    matrix.addPlayerMelds(player, meldInfo, False) 

                # bug if i have else instead of this elif in a very specific case (see round 1)
                elif arr[index-2][0] != "N":
                    matrix.addPlayerMelds(player, meldInfo, True) 
                    matrix.addClosedKan(player)

                else: 
                    matrix.setOpen(player)
                    matrix.addPlayerMelds(player, meldInfo, False) 

                #chi:0, pon:1, openKan:2, closedKain:3, chakan:4
                matrix.addMeldNum(player, meldInfo[1])
 
            # if new dora then adds it
            elif item[0] == "DORA":
                matrix.addDoraIndicator( int(attr["hai"]) // 4 )

            elif (item[0] == "REACH") and attr["step"] == "2":
                points = [int(i) for i in attr["ten"].split(",")]
                matrix.setPlayerScore(points) 


        else:
            #### DRAWS ####
            attr = item[0]             # attr in the form of, say, T46
            moveIndex = attr[0]        # T
            tile = int(attr[1:]) // 4  # 46 // 4
            if moveIndex == "T":
                matrix.setLastDrawPlayer(0)   
                hand = matrix.getPrivateHand(0)
                matrix.decWallTiles()   # remove a wall tile after drawing
                matrix.addTilePrivateHand(0, tile)      # add the drawn tile to hand

                checkRiichi(0)

            elif moveIndex == "U":
                matrix.setLastDrawPlayer(1)                   
                hand = matrix.getPrivateHand(1)

                matrix.decWallTiles()             
                matrix.addTilePrivateHand(1, tile)
                
                checkRiichi(1) 

            elif moveIndex == "V":
                matrix.setLastDrawPlayer(2)   
                hand = matrix.getPrivateHand(2)

                matrix.decWallTiles()        
                matrix.addTilePrivateHand(2, tile) 
                
                checkRiichi(2)
  
            elif moveIndex == "W":
                matrix.setLastDrawPlayer(3)   
                hand = matrix.getPrivateHand(3)

                matrix.decWallTiles()           
                matrix.addTilePrivateHand(3, tile)  
                
                checkRiichi(3)

            #### DISCARDS #### 
            elif moveIndex == "D":
                matrix.setLastDiscardPlayer(0)
                matrix.removeTilePrivateHand(0, tile)   # remove discarded tile from hand 
                matrix.setLastDiscardTile(tile)
                # If discarded tile doesn't get called, then adds it to pool
                if arr[index+1][0] != "N":
                    matrix.addPlayerPool(0, tile)

            elif moveIndex == "E":
                matrix.setLastDiscardPlayer(1)
                matrix.removeTilePrivateHand(1, tile)  
                matrix.setLastDiscardTile(tile)
                if arr[index+1][0] != "N":
                    matrix.addPlayerPool(1, tile)

            elif moveIndex == "F":
                matrix.setLastDiscardPlayer(2)
                matrix.removeTilePrivateHand(2, tile) 
                matrix.setLastDiscardTile(tile)
                if arr[index+1][0] != "N":
                    matrix.addPlayerPool(2, tile)
                
            elif moveIndex == "G":
                matrix.setLastDiscardPlayer(3)
                matrix.removeTilePrivateHand(3, tile)
                matrix.setLastDiscardTile(tile)
                if arr[index+1][0] != "N":
                    matrix.addPlayerPool(3, tile)

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

out = [convertLog(log) for log in logs]

wind_arr = ["e", "s", "w", "n"]

def num_to_wind(integer):
    return wind_arr[integer]

def printNice(game):
    int_game = [[int(element) for element in row] for row in game]
    game=int_game
    print("round wind: ", game[0][0], "| dealer: ", game[0][1], "| tilesInWall: ", game[0][5], "| doras: ", webFormat(game[1]), "| roundNum: ", game[0][33], "| honba sticks: ", game[0][3], "| riichi sticks: ", game[0][4],"| scores", game[0][6:10])
    print("POV wind: "+ windDict[ game[0][2] ]+ " | POVHand: ", webFormat(game[2]))  

    for i in range(4):
        print("player"+str(i)+ "| #chi=", game[0][14+i], "| #pon=", game[0][18+i], "| #kan=", game[0][22+i], "| #isOpen=", game[0][26+i],"| melds: "+webFormat(game[3+i]))
    for i in range(4):
        print("player"+str(i)+" pool: ",webFormat(game[7+i]))


tupl = out[3]
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

