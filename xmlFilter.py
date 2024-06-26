
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


strToIndex = {
        "1m": 0,
        "2m": 1,
        "3m": 2,
        "4m": 3,
        "5m": 4,
        "6m": 5,
        "7m": 6,
        "8m": 7,
        "9m": 8,
        "1p": 9,
        "2p": 10,
        "3p": 11,
        "4p": 12,
        "5p": 13,
        "6p": 14,
        "7p": 15,
        "8p": 16,
        "9p": 17,
        "1s": 18,
        "2s": 19,
        "3s": 20,
        "4s": 21,
        "5s": 22,
        "6s": 23,
        "7s": 24,
        "8s": 25,
        "9s": 26,
        "E": 27,
        "S": 28,
        "W": 29,
        "N": 30,
        "Wd": 31,
        "Gd": 32,
        "Rd": 33
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
                newArr.append("E draw: " + indexToStr[(int(item[0][1:]) // 4)])

            elif item[0][0] == "U":
                newArr.append("S draw: " + indexToStr[(int(item[0][1:]) // 4)])

            elif item[0][0] == "V":
                newArr.append("W draw: " + indexToStr[(int(item[0][1:]) // 4)])
                
            elif item[0][0] == "W":
                newArr.append("N draw: " + indexToStr[(int(item[0][1:]) // 4)])
            

            if item[0][0] == "D":
                newArr.append("E discard: " + indexToStr[(int(item[0][1:]) // 4)])

            elif item[0][0] == "E":
                newArr.append("S discard: " + indexToStr[(int(item[0][1:]) // 4)])

            elif item[0][0] == "F":
                newArr.append("W discard: " + indexToStr[(int(item[0][1:]) // 4)])
                
            elif item[0][0] == "G":
                newArr.append("N discard: " + indexToStr[(int(item[0][1:]) // 4)])

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





