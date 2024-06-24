
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

print(rough_string, "\n\n\n")

root = ET.fromstring(rough_string)

# Initialize an empty dictionary to store headers and their attributes
headers_dict = {}

arr = []

for element in root:

    header_name = element.tag
    
    attributes_dict = element.attrib

    arr.append((header_name ,  attributes_dict))

print(arr)

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
    out=np.zeros(34, dtype=int)
    string_list = string.split(",")
    array = np.array([int(i) for i in string_list])
    for i in array:
        out[i // 4] +=1
    return webFormat(out)






for item in arr:
    if item[1]:

        if item[0] == "INIT":
            attr = item[1]

            print("Intialise", format_xmlHand(attr["hai0"]) , format_xmlHand(attr["hai1"]) , format_xmlHand(attr["hai2"]) , format_xmlHand(attr["hai3"]))

        if item[0] == "N":
            attr = item[1]
            player = playerDict[int(attr["who"])]
            meld = attr["m"]

            print(player, "CALLS", meld)
        
        print(item[0], item[1])
    else:

        if item[0][0] == "T":
            print("e draw", indexToStr[(int(item[0][1:]) // 4)])

        elif item[0][0] == "U":
            print("s draw", indexToStr[(int(item[0][1:]) // 4)])

        elif item[0][0] == "V":
            print("w draw", indexToStr[(int(item[0][1:]) // 4)])
            
        elif item[0][0] == "W":
            print("n draw", indexToStr[(int(item[0][1:]) // 4)])
        

        if item[0][0] == "D":
            print("e discard", indexToStr[(int(item[0][1:]) // 4)])

        elif item[0][0] == "E":
            print("s discard", indexToStr[(int(item[0][1:]) // 4)])

        elif item[0][0] == "F":
            print("w discard", indexToStr[(int(item[0][1:]) // 4)])
            
        elif item[0][0] == "G":
            print("n discard", indexToStr[(int(item[0][1:]) // 4)])


# print("\n ")
# print(firstGame)







