
import json
import random
import numpy as np
from numpy.typing import NDArray

import pprint

from xml.dom import minidom
import xml.etree.ElementTree as ET

import xmltodict 

import bz2
import sqlite3
from lxml import etree
from tqdm import tqdm

import sqlite3

dbfile = '2020.db'

con = sqlite3.connect(dbfile)

cur = con.cursor()

res = cur.execute("SELECT log_id, log_content FROM logs")

log = res.fetchone()

firstgame = log[0]

firstBlob = log[1]

print(firstgame)

print("\n")


print("\n")

con.close()

XML = etree.XML

decompress = bz2.decompress

content = decompress(firstBlob)

xml = XML(content, etree.XMLParser(recover=True))

rough_string = ET.tostring(xml, encoding='unicode')

#print(rough_string)

root = ET.fromstring(rough_string)

# Initialize an empty dictionary to store headers and their attributes
headers_dict = {}

for element in root:

    header_name = element.tag
    
    attributes_dict = element.attrib
    
    headers_dict[header_name] = attributes_dict

# Print the dictionary
# print(headers_dict)

for key in headers_dict:
    if headers_dict[key]:

        if key == "INIT":
            print("Intialise")

        print(key, headers_dict[key])
    else:

        #tile 

        print(key)

# print("\n ")
# print(firstGame)


class Game:

    windDict = {
        "e_wind": 0,
        "s_wind": 1,
        "w_wind": 2,
        "n_wind": 3,
    }

    strToIndex = {
        "1_char": 0,
        "2_char": 1,
        "3_char": 2,
        "4_char": 3,
        "5_char": 4,
        "6_char": 5,
        "7_char": 6,
        "8_char": 7,
        "9_char": 8,
        "1_circ": 9,
        "2_circ": 10,
        "3_circ": 11,
        "4_circ": 12,
        "5_circ": 13,
        "6_circ": 14,
        "7_circ": 15,
        "8_circ": 16,
        "9_circ": 17,
        "1_bamb": 18,
        "2_bamb": 19,
        "3_bamb": 20,
        "4_bamb": 21,
        "5_bamb": 22,
        "6_bamb": 23,
        "7_bamb": 24,
        "8_bamb": 25,
        "9_bamb": 26,
        "e_wind": 27,
        "s_wind": 28,
        "w_wind": 29,
        "n_wind": 30,
        "w_drag": 31,
        "g_drag": 32,
        "r_drag": 33
    }

    indexToStr = {v: k for k, v in strToIndex.items()}

    def __init__(self):

        self.gameState = np.zeros((11, 34))
    
    #gamestate conversion functions:

    def setRoundWind(self, wind):
        windNum = Game.windDict[wind]
        self.gameState[0][0] = windNum

    def getRoundWind(self):
        reversedWindDict = {v: k for k, v in Game.windDict.items()}
        return reversedWindDict[self.gameState[0][0]]
    

    def setDealer(self, dealer):
        self.gameState[0][1] = dealer
    
    def getDealer(self):
        return self.gameState[0][1]

    def setHonbaSticks(self, amount):
        self.gameState[0][3] = amount
    
    def getHonbaSticks(self):
        return self.gameState[0][3]
    
    def setRiichiSticks(self, amount):
        self.gameState[0][4] = amount
    
    def getRiichiSticks(self):
        return self.gameState[0][4]
    
    def setWallTiles(self, amount):
        self.gameState[0][5] = amount
    
    def decWallTiles(self):
        self.gameState[0][5] -=1

    def getWallTiles(self):
        return self.gameState[0][5]
    
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
    
    def addDoraIndicator(self, doraIndicator: str):
        self.gameState[1][self.strToIndex[doraIndicator]] += 1
    
    def getDoraIndicators(self):
        return self.vectorToReadable(self.gameState[1])
    
    @staticmethod
    def readableToVector(readableHand: list):
        vectorHand = np.zeros(34)
        for i in readableHand:
            vectorHand[Game.strToIndex[i]] += 1
        return vectorHand
    
    @staticmethod
    def vectorToReadable(vectorHand: NDArray):
        readableHand = []
        for i in range(34):
            for j in range(int(vectorHand[i])):
                readableHand.append(Game.indexToStr[i])
        return readableHand
    
    #game action functions:

    def draw(self):
        availableTile = list(self._tileWall.keys())
        numAvailable = list(self._tileWall.values())

        drawnTile = random.choices(availableTile, weights=numAvailable, k=1)[0]
        self._tileWall[drawnTile] -= 1
        return drawnTile
























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
    out=np.zeros(34, dtype=int)
    string_list = string.split(",")
    array = np.array([int(i) for i in string_list])
    for i in array:
        out[i // 4] +=1
    return webFormat(out)




