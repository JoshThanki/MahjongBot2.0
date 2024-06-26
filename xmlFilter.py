
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

# strToIndex = {
#         "1_char": 0,
#         "2_char": 1,
#         "3_char": 2,
#         "4_char": 3,
#         "5_char": 4,
#         "6_char": 5,
#         "7_char": 6,
#         "8_char": 7,
#         "9_char": 8,
#         "1_circ": 9,
#         "2_circ": 10,
#         "3_circ": 11,
#         "4_circ": 12,
#         "5_circ": 13,
#         "6_circ": 14,
#         "7_circ": 15,
#         "8_circ": 16,
#         "9_circ": 17,
#         "1_bamb": 18,
#         "2_bamb": 19,
#         "3_bamb": 20,
#         "4_bamb": 21,
#         "5_bamb": 22,
#         "6_bamb": 23,
#         "7_bamb": 24,
#         "8_bamb": 25,
#         "9_bamb": 26,
#         "e_wind": 27,
#         "s_wind": 28,
#         "w_wind": 29,
#         "n_wind": 30,
#         "w_drag": 31,
#         "g_drag": 32,
#         "r_drag": 33
#     }

# indexToStr = {v: k for k, v in strToIndex.items()}

tile_dic = {i: f"{i+1}_man" if i <= 8 else f"{i-8}_pin" if i <= 17 else f"{i-17}_sou" for i in range(27)}
honour_entries = {27 : "East", 28 : "South", 29 : "West", 30 : "North", 31 : "White", 32 : "Green", 33 : "Red"}
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

def printNice(arr):
    newArr = []
    for item in arr:
        if item[1]:

            if item[0] == "INIT":
                attr = item[1]

                points = attr["ten"].split(",")

                newArr.append("Initialise: Dealer " + attr["oya"] + " | East player, score " + points[0] + ", hand " + format_xmlHand(attr["hai0"]) + " |  South player,  score  " + points[1] + ", hand " + format_xmlHand(attr["hai1"]) + " | West player,  score " + points[2] + ", hand " + format_xmlHand(attr["hai2"]) + " | North player,  score " + points[3] + ", hand " + format_xmlHand(attr["hai3"]))
                newArr.append((item[0], item[1]))

            elif item[0] == "N":
                attr = item[1]
                player = playerDict[int(attr["who"])]
                meld = attr["m"]

                newArr.append(player + " " + "CALLS" + " " + meld)
            
            else:
                newArr.append((item[0], item[1]))
        else:

            if item[0][0] == "T":
                newArr.append("e draw" + " " + tile_dic[(int(item[0][1:]) // 4)])

            elif item[0][0] == "U":
                newArr.append("s draw" + " " + tile_dic[(int(item[0][1:]) // 4)])

            elif item[0][0] == "V":
                newArr.append("w draw" + " " + tile_dic[(int(item[0][1:]) // 4)])
                
            elif item[0][0] == "W":
                newArr.append("n draw" + " " + tile_dic[(int(item[0][1:]) // 4)])
            

            if item[0][0] == "D":
                newArr.append("e discard" + " " + tile_dic[(int(item[0][1:]) // 4)])

            elif item[0][0] == "E":
                newArr.append("s discard" + " " + tile_dic[(int(item[0][1:]) // 4)])

            elif item[0][0] == "F":
                newArr.append("w discard" + " " + tile_dic[(int(item[0][1:]) // 4)])
                
            elif item[0][0] == "G":
                newArr.append("n discard" + " " + tile_dic[(int(item[0][1:]) // 4)])

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


    arr = printNice(arr)

    return game, arr


out = [covertLog(log) for log in logs]

with open("out.txt", "w+") as file:
    json.dump(out, file, indent = 2)





