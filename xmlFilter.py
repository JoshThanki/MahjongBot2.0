
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

# Parse the rough string with minidom
dom = minidom.parseString(rough_string)

# Pretty-print the XML string with indentation
pretty_xml_string = dom.toprettyxml()

# Print the pretty XML string
# print(pretty_xml_string)

# dic = xmltodict.parse(rough_string)

# # firstGame = [dic[item][0] for item in dic.keys()] 

# with open("out.txt", "w+") as file:
#     json.dump(dic, file, indent=2)


# root = ET.fromstring(rough_string)

# # List to store headers
# headers = []

# # Iterate through all elements in the XML
# for elem in root.iter():
#     # Append the tag of each element to the headers list
#     headers.append(elem.tag)

# # Print the headers list
# print(headers)



# Parse the XML string
root = ET.fromstring(rough_string)

# List to store headers and their data
headers_and_data = []

# Iterate through all elements in the XML
for elem in root.iter():
    # Get the tag and text of each element
    tag = elem.tag
    text = elem.text.strip() if elem.text else ''  # Strip any leading/trailing whitespace
    
    # Append a tuple of tag and text to the list
    headers_and_data.append((tag, text))

# Print the headers and their data
for tag, text in headers_and_data:
    print(f'Header: {tag}, Data: {text}')


# print("\n ")
# print(firstGame)

#Creates a dictionary containing an entire set of tiles

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




