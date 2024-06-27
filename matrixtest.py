
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

for i in range(1):
    logs.append(res.fetchone())

con.close()

out = {}



tile_dic = {i: f"{i+1}m" if i <= 8 else f"{i-8}p" if i <= 17 else f"{i-17}s" for i in range(27)}
honour_entries = {27 : "e", 28 : "s", 29 : "w", 30 : "n", 31 : "wd", 32 : "gd", 33 : "rd"}
tile_dic.update(honour_entries)


playerDict = {
        0 : "e",
        1 : "s",
        2: "w",
        3 : "n"
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
    k=0
    for suit in handArray:
        if sum(suit) == 0:
            k+=1
            continue
        for num in range(len(suit)):
            if suit[num] == 0:
                continue
            else:
                string += str(num+1)*suit[num]

        string += dict[k]
        k+=1

    return string

def format_xmlHand(string):
    if string == "":
        return ""

    out=np.zeros(34, dtype=int)
    string_list = string.split(",")
    array = np.array([int(i) for i in string_list])
    for i in array:
        out[i // 4] +=1
    return webFormat(out)


class Matrix:
    windDict = {
        "e":0,
        "s": 1,
        "w": 2,
        "n": 3,
    }
    
    tile_dic = {i: f"{i+1}m" if i <= 8 else f"{i-8}p" if i <= 17 else f"{i-17}s" for i in range(27)}
    honour_entries = {27 : "e", 28 : "s", 29 : "w", 30 : "n", 31 : "wd", 32 : "gd", 33 : "rd"}
    tile_dic.update(honour_entries)

    revtile_dic = {v: k for k, v in tile_dic.items()}
            
    def __init__(self):

        self.gameState = np.zeros((11, 34))
        self.privateHands = [[0]*34 , [0]*34 , [0]*34 , [0]*34]
        self.Closed = [True, True, True, True]
        self.notRiichi = [True, True, True, True]
        self.winds = [0,1,2,3]
        
        #set last player discard back to padding
        self.setPlayerLastDiscard(-128, -128)
        self.initialisePadding()
    
    def getnotRiichi(self, player):
        return self.notRiichi[player]
    
    def setRiichi(self, player):
        self.notRiichi[player] = False


    def getMatrix(self):
        return self.gameState
    
    #clears everything other than metadata  (need to fix padding, will do later)
    def clearMatrix(self):
        self.gameState[1:] = np.zeros((10, 34))
    
    # hand [34]

    def initialisePadding(self):
        self.gameState[0][25:32] = [0] * 7 

    def initialisePrivateHands(self, hands):
        for player in range(4):
            self.privateHands[player] = hands[player]
   
    def setPrivatehand(self, player, hand):
        self.gameState[2] = hand

    #input player (0-3) tile (0-34)
    def addTilePrivateHand(self, player, tile):
        self.privateHands[player][tile] += 1

    #input player (0-3) tile (0-34)
    def removeTilePrivateHand(self, player, tile):
        self.privateHands[player][tile] -= 1

    def getPrivateHand(self, player):
        return self.privateHands[player]
    
    #input - 0,1,2,3
    def setRoundWind(self, wind):
        self.gameState[0][0] = wind

    def getRoundWind(self):
        return self.gameState[0][0]
    
    #input 0,1,2,3
    def setDealer(self, dealer):
        self.gameState[0][1] = dealer
    
    def getDealer(self):
        return self.gameState[0][1]


    #input player (0-3)
    def setPOVPlayer(self, player):
        self.gameState[0][2] = player
        self.gameState[2] = self.privateHands[player]
        self.gameState[0][16] = self.winds[player]

    def rotPOVPlayer(self):
        self.gameState[0][2] = (self.gameState[0][2] + 1) % 3
        self.gameState[2] = self.privateHands[self.gameState[0][2]]
        self.gameState[0][16] =  self.gameState[16] - 1 if self.gameState[16] else 2

    #input amount 
    def setHonbaSticks(self, amount):
        self.gameState[0][3] = amount
    
    def getHonbaSticks(self):
        return self.gameState[0][3]
    
    #input amount
    def setRiichiSticks(self, amount):
        self.gameState[0][4] = amount
    
    def addRiichiSticks(self):
        self.gameState[0][4]+=1
    
    def getRiichiSticks(self):
        return self.gameState[0][4]
    
    #input amount
    def setWallTiles(self):
        self.gameState[0][5] = 69
    
    #decrement wall tiles by one
    def decWallTiles(self):
        self.gameState[0][5] -=1

    def getWallTiles(self):
        return self.gameState[0][5]
    
    #input score [4]
    def setPlayerScore(self, score):
        for player in [0,1,2,3]:
            self.gameState[0][6+player] = score[player]
    
    def getPlayerScore(self, player):
        if player in [0,1,2,3]:
            return self.gameState[0][6+player]
        else:
            print("Invalid Player")


    #input player, sets riichi status to true
    def setPlayerRiichi(self, player):
        if player in [0,1,2,3]:
            self.gameState[0][10+player] = 1
        else:
            print("Invalid Player")
    
    def getPlayerRiichiStat(self, player):
        if player in [0,1,2,3]:
            return self.gameState[0][10+player]
        else:
            print("Invalid Player")
    
    #input player (0-3), tile (0-34)
    def setPlayerLastDiscard(self, player, tile):
        self.gameState[0][14] = tile
        self.gameState[0][15] = player

    #returns player and tile
    def getPlayerLastDiscard(self):
        return int(self.gameState[0][15]), int(self.gameState[0][14])
    
    #input player (0-3), wind(0-3)
    def setPlayerWind(self, player, wind):
        self.gameState[0][16+player] = wind

    #input tile (0-34)
    def addDoraIndicator(self, doraIndicator):
        self.gameState[1][doraIndicator] += 1
    
    def getDoraIndicators(self):
        return (self.gameState[1])
    
    #input player (0-3), meldinfo(([3-4] , (0-3) 0: chi,  1: pon, 2: open kan, 3: closed kan

    def addPlayerMelds(self, player, meldinfo):
        tiles = meldinfo[0]
        type = meldinfo[1]

        if not type:
            self.gameState[0][17+player] += 1
        else:
            self.gameState[0][21+player]+=1

        for tile in tiles:
            self.gameState[3+player][tile] +=1
    
    def addTileToPlayerPool(self, player, tile):
        self.gameState[7+player][tile] += 1


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
            if t == 0: return (h[tile+1] and h[tile+2])
            elif t == 8: return (h[tile-1] and h[tile-2])
            elif t == 1: return (h[tile+1] and h[tile+2]) or (h[tile-1] and h[tile+1])
            elif t == 7: return (h[tile-1] and h[tile-2]) or (h[tile-1] and h[tile+1])
            else: return (h[tile-1] and h[tile-2]) or (h[tile-1] and h[tile+1]) or (h[tile+1] and h[tile+2])
    
    def setOpen(self, player):
        self.Closed[player] = False
    
    def getClosed(self, player):
        return self.Closed[player]

def matprint(mat, fmt="g"):
    col_maxes = [max([len(("{:"+fmt+"}").format(x)) for x in col]) for col in mat.T]
    for x in mat:
        for i, y in enumerate(x):
            print(("{:"+str(col_maxes[i])+fmt+"}").format(y), end="  ")
        print("")



def matrixifymelds(arr):
    matrix = Matrix()

    chiArr = []
    ponArr = []
    kanArr = []

    def format_xmlHand(string):
        if string == '':
            return [0]*34

        out=np.zeros(34, dtype=int)
        string_list = string.split(",")
        array = np.array([int(i) for i in string_list])
        for i in array:
            out[i // 4] +=1
        return out

    def format_seed(string):
        return [int(i)//4 for i in string.split(",")]


    def checkMelds():
        discardPlayer, tile = matrix.getPlayerLastDiscard() 
        players = [0,1,2,3]
        players.remove(discardPlayer)

        chiArr, ponArr, kanArr  = None , None, None

        for player in players:
            matrix.setPOVPlayer(player)
            chi, pon, kan = 0 , 0 , 0 
            
            previousPlayer = ((player - 1) if player else 2)

            if discardPlayer == previousPlayer and matrix.canChi(player, tile):
                if arr[index+1][0] == "N" and int(arr[index+1][1]["who"]) == player: #Add code to check actual chi
                    chi = 1

                chiArr = [copy.deepcopy(matrix.getMatrix()), chi]

            elif  matrix.canPon(player, tile):
                if arr[index+1][0] == "N" and int(arr[index+1][1]["who"]) == player: #Add code to check actual pon
                    pon = 1

                ponArr = [copy.deepcopy(matrix.getMatrix()), pon]

            elif  matrix.canKan(player, tile):
                if arr[index+1][0] == "N" and int(arr[index+1][1]["who"]) == player: #Add code to check actual kan
                    kan = 1

                ponArr = [copy.deepcopy(matrix.getMatrix()), kan]


        matrix.setPOVPlayer(discardPlayer)
        
        return chiArr, ponArr, kanArr


    for index,item in enumerate(arr): 
        if item[1]:
            attr = item[1]
            if item[0] == "INIT":
                latestDiscard = 0
                matrix.clearMatrix() 

                matrix.setWallTiles()
                
                points = attr["ten"].split(",")
                
                matrix.setPlayerScore(points)
                
                matrix.setDealer(attr["oya"])

                initialHands = [format_xmlHand(attr["hai"+str(i)]) for i in range(4) ]
                matrix.initialisePrivateHands(initialHands)

                seed = format_seed(attr["seed"])
                matrix.addDoraIndicator(seed[5])
                matrix.setHonbaSticks(seed[1])

            elif item[0] == "N":
                meldTiles, isChi, newDora = [1,1,1],0,0    #decodeMeld(attr["m"]) #placholder function
                player = int( attr["who"] )

                #matrix.setOpen(player)
            
#            else:
#                newArr.append((item[0], item[1]))

        else:
            attr = item[0]        # attr in the form of, say, T46
            moveIndex = attr[0]   # T
            tile = int(attr[1:]) // 4  # 46 // 4

            if moveIndex == "T":
                matrix.decWallTiles()                          # remove a wall tile after drawing
                matrix.addTilePrivateHand(0, tile)   # add the drawn tile to hand

            elif moveIndex == "U":
                matrix.decWallTiles()
                matrix.addTilePrivateHand(1, tile)
                
            elif moveIndex == "V":
                matrix.decWallTiles()
                matrix.addTilePrivateHand(2, tile)
                
            elif moveIndex == "W":
                matrix.decWallTiles()
                matrix.addTilePrivateHand(3, tile)
                

            elif moveIndex == "D":
                matrix.removeTilePrivateHand(0, tile)   # remove discarded tile from hand 
                matrix.setPlayerLastDiscard(0, tile)  # updates latest discard
                chiRet, ponRet, kanRet = checkMelds()  
                if chiRet:
                    chiArr.append(chiRet)
                elif ponRet:
                    ponArr.append(ponRet)
                elif kanRet:
                    kanArr.append(kanRet)

            elif moveIndex == "E":
                matrix.removeTilePrivateHand(1, tile)  
                matrix.setPlayerLastDiscard(1, tile)
                chiRet, ponRet, kanRet = checkMelds() 

                if chiRet:
                    chiArr.append(chiRet)
                elif ponRet:
                    ponArr.append(ponRet)
                elif kanRet:
                    kanArr.append(kanRet)
                

            elif moveIndex == "F":
                matrix.removeTilePrivateHand(2, tile) 
                matrix.setPlayerLastDiscard(2, tile)
                chiRet, ponRet, kanRet = checkMelds() 
                
                if chiRet:
                    chiArr.append(chiRet)
                elif ponRet:
                    ponArr.append(ponRet)
                elif kanRet:
                    kanArr.append(kanRet)
                
            elif moveIndex == "G":
                matrix.removeTilePrivateHand(3, tile)
                matrix.setPlayerLastDiscard(3, tile)  
                chiRet, ponRet, kanRet = checkMelds() 

                if chiRet:
                    chiArr.append(chiRet)
                elif ponRet:
                    ponArr.append(ponRet)
                elif kanRet:
                    kanArr.append(kanRet)
                
    return chiArr, ponArr, kanArr



def matrixify(arr):
    matrix = Matrix()

    reachArr = []

    def format_xmlHand(string):
        if string == '':
            return [0]*34

        out=np.zeros(34, dtype=int)
        string_list = string.split(",")
        array = np.array([int(i) for i in string_list])
        for i in array:
            out[i // 4] +=1
        return out

    def format_seed(string):
        return [int(i)//4 for i in string.split(",")]

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



    for index,item in enumerate(arr): 
        if item[1]:
            attr = item[1]
            if item[0] == "INIT":
                latestDiscard = 0
                matrix.clearMatrix() 

                matrix.setWallTiles()
                
                points = attr["ten"].split(",")
             #   matrix.setPlayerScore(points)
                
                matrix.setDealer(attr["oya"])

                initialHands = [format_xmlHand(attr["hai"+str(i)]) for i in range(4) ]
                matrix.initialisePrivateHands(initialHands)

                seed = format_seed(attr["seed"])
                matrix.addDoraIndicator(seed[5])
                matrix.setHonbaSticks(seed[1])

            elif item[0] == "N":
                meldTiles, isChi, newDora = [1,1,1],0,0    #decodeMeld(attr["m"]) #placholder function
                player = int( attr["who"] )

                #matrix.setOpen(player)
            
#            else:
#                newArr.append((item[0], item[1]))

        else:
            attr = item[0]        # attr in the form of, say, T46
            moveIndex = attr[0]   # T
            tile = int(attr[1:]) // 4  # 46 // 4

            if moveIndex == "T":
                hand = matrix.getPrivateHand(0)

                matrix.decWallTiles()                          # remove a wall tile after drawing
                matrix.addTilePrivateHand(0, tile)   # add the drawn tile to hand
                matrix.setPrivatehand(0, hand)

                if matrix.getnotRiichi(0) and matrix.getClosed(0) and calcShanten(matrix.getPrivateHand(0)) == 0:
                    if arr[index+1][0] == "REACH": 
                        matrix.setRiichi(0)
                    print(arr[index+1])
                    print(calcShanten(hand))
                    print(webFormat(hand))
                    reachArr.append([copy.deepcopy(matrix.getMatrix()), 0 if matrix.getnotRiichi(0) else 1]) # riichi is always 1 for now


            elif moveIndex == "U":
                matrix.decWallTiles()
                matrix.addTilePrivateHand(1, tile)
                
            elif moveIndex == "V":
                matrix.decWallTiles()
                matrix.addTilePrivateHand(2, tile)
                
            elif moveIndex == "W":
                matrix.decWallTiles()
                matrix.addTilePrivateHand(3, tile)
                

            elif moveIndex == "D":
                matrix.removeTilePrivateHand(0, tile)   # remove discarded tile from hand 
                matrix.setPlayerLastDiscard = tile                             # updates latest discard

            elif moveIndex == "E":
                matrix.removeTilePrivateHand(1, tile)  
                matrix.setPlayerLastDiscard = tile  

            elif moveIndex == "F":
                matrix.removeTilePrivateHand(2, tile) 
                matrix.setPlayerLastDiscard = tile  
                
            elif moveIndex == "G":
                matrix.removeTilePrivateHand(3, tile)
                matrix.setPlayerLastDiscard = tile  

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

#with open("out.txt", "w+") as file:
#    json.dump(out, file, indent = 2)

tupl = out[0]
game = tupl[1]




def testMatrixifymelds(game):

    chiArr, ponArr, kanArr = matrixifymelds(game)

    for res in chiArr:
        print()
        print("matrix")
        matprint(res[0])
        print("label")
        print(res[1])

    # for res in ponArr:
    #     print()
    #     print("matrix")
    #     matprint(res[0])
    #     print("label")
    #     print(res[1])

    # for res in kanArr:
    #     print()
    #     print("matrix")
    #     matprint(res[0])
    #     print("label")
    #     print(res[1])


testMatrixifymelds(game)