
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

dbfile = '2020.db'

con = sqlite3.connect(dbfile)

cur = con.cursor()

res = cur.execute("SELECT log_id, log_content FROM logs")

logs = []

for i in range(3):
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
    
    def getMatrix(self):
        return self.gameState
    
    #clears everything other than metadata  (need to fix padding, will do later)
    def clearMatrix(self):
        self.gameState[1:] = np.zeros((10, 34))
    
    #input player (0-3) hand [34]
    def setPrivateHand(self, player, hand):
        self.privateHands[player] = hand

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
    def setPOVPlayer(self, player, wind):
        self.gameState[0][2] = player
        self.gameState[2] = self.privateHands[player]
        self.gameState[16] = wind

    def rotPOVPlayer(self):
        self.gameState[0][2] = (self.gameState[0][2] + 1) % 3
        self.gameState[2] = self.privateHands[self.gameState[0][2]]
        self.gameState[16] =  self.gameState[16] - 1 if self.gameState[16] else 2

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
    
    
    #input player 0-3 , score
    def setPlayerScore(self, player, score):
        if player in [0,1,2,3]:
            self.gameState[0][6+player] = score
        else:
            print("Invalid Player")
    
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

    #input player (0-3), wind(0-3)
    def setPlayerWind(self, player, wind):
        self.gameState[0][16+player] = wind

    #input tile (0-34)
    def addDoraIndicator(self, doraIndicator):
        self.gameState[1][doraIndicator] += 1
    
    def getDoraIndicators(self):
        return (self.gameState[1])
    
    #input player (0-3), meldinfo( ([3-4] , isChi)
    def addPlayerMelds(self, player, meldinfo):
        tiles = meldinfo[0]
        type = meldinfo[1]

        if type:
            self.gameState[0][17+player] += 1
        else:
            self.gameState[0][21+player]+=1

        for tile in tiles:
            self.gameState[3+player][tile] +=1
    
    def addTileToPlayerPool(self, player, tile):
        self.gameState[7+player][tile] += 1



def matrixify(arr):
    newArr = []

    matrix, privHands = Matrix()

    def format_xmlHand(string):
        out=np.zeros(34, dtype=int)
        string_list = string.split(",")
        array = np.array([int(i) for i in string_list])
        for i in array:
            out[i // 4] +=1
        return out

    for item in arr:
        if item[1]:

            if item[0] == "INIT":
                matrix.clear()

                attr = item[1]  

                matrix.setWallTiles()
                
                points = attr["ten"].split(",")
                matrix.setPlayerScore(points)
                
                matrix.setDealer(attr["oya"])

                initialHands = [format_xmlHand(attr["hai"+str(i)]) for i in range(4) ]
                privHands.setPrivateHand(initialHands)

            elif item[0] == "N":
                attr = item[1]
                player = playerDict[int(attr["who"])]
                meld = attr["m"]

                newArr.append(player + " " + "CALLS" + " " + meld)
            
            else:
                newArr.append((item[0], item[1]))
        else:

            if item[0][0] == "T":
                newArr.append("p0 draw" + " " + tile_dic[(int(item[0][1:]) // 4)])

            elif item[0][0] == "U":
                newArr.append("p1 draw" + " " + tile_dic[(int(item[0][1:]) // 4)])

            elif item[0][0] == "V":
                newArr.append("p2 draw" + " " + tile_dic[(int(item[0][1:]) // 4)])
                
            elif item[0][0] == "W":
                newArr.append("p3 draw" + " " + tile_dic[(int(item[0][1:]) // 4)])
            

            if item[0][0] == "D":
                newArr.append("p0 discard" + " " + tile_dic[(int(item[0][1:]) // 4)])

            elif item[0][0] == "E":
                newArr.append("p1 discard" + " " + tile_dic[(int(item[0][1:]) // 4)])

            elif item[0][0] == "F":
                newArr.append("p2 discard" + " " + tile_dic[(int(item[0][1:]) // 4)])
                
            elif item[0][0] == "G":
                newArr.append("p3 discard" + " " + tile_dic[(int(item[0][1:]) // 4)])

    return newArr


def covertLog(log):

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


    arr = matrixify(arr)

    return game, arr


out = [covertLog(log) for log in logs]

with open("out.txt", "w+") as file:
    json.dump(out, file, indent = 2)





