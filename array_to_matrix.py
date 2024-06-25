import random
import numpy as np
from numpy.typing import NDArray

from xml.dom import minidom
import xml.etree.ElementTree as ET

import bz2
import sqlite3
from lxml import etree
from tqdm import tqdm
import re

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




def str_to_num(num_str):
    num_list = re.split(r'[,\s;|]+', num_str)
    return [int(num) for num in num_list]


Game_Matrix = np.zeros((11,34))
POV_0_Hand = np.zeros(34)
POV_1_Hand = np.zeros(34)
POV_2_Hand = np.zeros(34)
POV_3_Hand = np.zeros(34)

for item in arr:
    if item[1]:

        if item[0] == "INIT":
            attr = item[1]
            Hand_0 = str_to_num(attr["hai0"])
            for j in range (len(Hand_0)):
                POV_0_Hand[Hand_0[j] // 4] += 1
            Hand_1 = str_to_num(attr["hai1"])
            for j in range (len(Hand_1)):
                POV_1_Hand[Hand_1[j] // 4] += 1
            Hand_2 = str_to_num(attr["hai2"])
            for j in range (len(Hand_2)):
                POV_2_Hand[Hand_2[j] // 4] += 1
            Hand_3 = str_to_num(attr["hai3"])
            for j in range (len(Hand_3)):
                POV_3_Hand[Hand_3[j] // 4] += 1
            score = str_to_num(attr["ten"])
            for i in range (len(score)):
                Game_Matrix[0][7+i]= score[i]*100

        
    else:

        if item[0][0] == "T":
            POV_0_Hand[(int(item[0][1:]) // 4)] += 1

        elif item[0][0] == "U":
            POV_1_Hand[(int(item[0][1:]) // 4)] += 1

        elif item[0][0] == "V":
            POV_2_Hand[(int(item[0][1:]) // 4)] += 1
            
        elif item[0][0] == "W":
            POV_3_Hand[(int(item[0][1:]) // 4)] += 1
        

        if item[0][0] == "D":
            POV_0_Hand[(int(item[0][1:]) // 4)] -= 1
            Game_Matrix[7][(int(item[0][1:]) // 4)] += 1

        elif item[0][0] == "E":
            POV_1_Hand[(int(item[0][1:]) // 4)] -= 1
            Game_Matrix[8][(int(item[0][1:]) // 4)] += 1

        elif item[0][0] == "F":
            POV_2_Hand[(int(item[0][1:]) // 4)] -= 1
            Game_Matrix[9][(int(item[0][1:]) // 4)] += 1
            
        elif item[0][0] == "G":
            POV_3_Hand[(int(item[0][1:]) // 4)] -= 1
            Game_Matrix[10][(int(item[0][1:]) // 4)] += 1