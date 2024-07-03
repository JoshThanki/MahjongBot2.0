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

#global functions
from Global import *


dbfile = 'es4p.db'
con = sqlite3.connect(dbfile)
cur = con.cursor()
res = cur.execute(f"SELECT log_id, log_content FROM logs")

#redefine numGames so don't cook my computer
NUMGAMES = 300

logs = []
for i in range(NUMGAMES):
    logs.append(res.fetchone())

con.close()

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
    def buildMatrix(self, player, forMeld=False, forClosedMeld=False, callTile=None):
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


        # sets call tile for the meld matrices
        if forMeld:
            if forClosedMeld:
                self.gameState[0][30] = callTile
            else:
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

    def canChi(self, player, tile): 
        #checks whether it's a honour tile
        if tile//9 == 3: return False
        else:
            #number of the tile
            t = tile % 9
            #hand of player
            h = self.privateHands[player]
            
            #if tileNum is 1
            if t == 0: return (h[tile+1]>0 and h[tile+2]>0)
            #if tileNum is 9
            elif t == 8: return (h[tile-1]>0 and h[tile-2]>0)
            #if tileNum is 2
            elif t == 1: return (h[tile+1]>0 and h[tile+2]>0) or (h[tile-1]>0 and h[tile+1]>0)
            #if tileNum is 8
            elif t == 7: return (h[tile-1]>0 and h[tile-2]>0) or (h[tile-1]>0 and h[tile+1]>0)
            # else:  3 <= tileNum <= 7 so can make any chi with it
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


    def handleMeld(self, player, meldInfo, isClosedCall):
        meldTiles = meldInfo[0]
        meldType = meldInfo[1]

        # (ordering of if and elif is important here)
        # handles chakan
        if meldType == 3: 
            self.decPlayerPonTiles(player, meldTiles)
            self.decPon(player)
            self.playerMelds[player][ meldTiles[0] ] = 4
            self.addKan(player)
            self.privateHands[player][ meldTiles[0] ] = 0
       
        # handles closed kan       
        elif isClosedCall:
            self.privateHands[player][ meldTiles[0] ] = 0
            self.addKan(player)
            self.playerMelds[player][ meldTiles[0] ] = 4

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
        callPlayer = None
        # true if next call is Pon or Kan; they get priority over chi.
        isPonInPriotity = lambda player: False
       
        nextMove  = arr[index+1]
        isNextMoveCall = (nextMove[0] == "N")

        isNextCallChi, isNextCallPon, isNextCallKan = False, False, False

        if isNextMoveCall:
            meldType = decodeMeld( int(nextMove[1]["m"]) )[1]
            callPlayer = int(nextMove[1]["who"])

            isNextCallChi = (meldType==0)
            isNextCallPon = (meldType==1)
            isNextCallKan = (meldType==2)

            isPonInPriotity = lambda player:  (isNextCallPon or isNextCallKan) and (player != CallPlayer)
       
        for player in players:
            chiLabel, ponLabel, kanLabel = 0, 0, 0

            previousPlayer = (player+3)%4
            isValidChiPlayer =  (discardPlayer == previousPlayer)
            isCurrentPlayer_NotInRiichi = matrix.getnotRiichi(player)
    
            isCurrentPlayerCallPlayer = (callPlayer == player)

            ### CHI ###
            if isValidChiPlayer and matrix.canChi(player, tile) and isCurrentPlayer_NotInRiichi and (not isPonInPriotity(player)):
                matrix.buildMatrix(player=player, forMeld=True)
                # if the player calls the tile and the call is chi
                if isNextCallChi and isCurrentPlayerCallPlayer: 
                    chiLabel = 1
                    # removes the tile from the wall since it got called
                    matrix.decPlayerPool(discardPlayer, tile)

                chiArr.append([copy.deepcopy(matrix.getMatrix()), chiLabel])

            ### PON ### 
            if matrix.canPon(player, tile) and isCurrentPlayer_NotInRiichi:
                matrix.buildMatrix(player=player, forMeld=True)
                if isNextCallPon and isCurrentPlayerCallPlayer: 
                    ponLabel = 1
                    matrix.decPlayerPool(discardPlayer, tile)
                ponArr.append([copy.deepcopy(matrix.getMatrix()), ponLabel])

            ### KAN ###
            if matrix.canKan(player, tile) and isCurrentPlayer_NotInRiichi:
                matrix.buildMatrix(player, forMeld=True)
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
                callTile = tile
                matrix.buildMatrix(player=drawPlayer, forMeld=True, forClosedMeld=True, callTile=callTile)
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
                callTile = tile
                matrix.buildMatrix(player=drawPlayer, forMeld=True, forClosedMeld=True, callTile=callTile)
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
                isClosedCall = (player == matrix.getLastDrawPlayer()) and arr[index-2][0] != "N"

                matrix.handleMeld(player, meldInfo, isClosedCall)
          
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
            matrix.buildMatrix(player=p)
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
    
    if arr:

        arr_np = np.array(arr)
        
        if statetype == 0:
            directory = os.path.join(".", "Data", str(year), "Riichi")
        elif statetype == 1:
            directory = os.path.join(".", "Data", str(year), "Chi")
        elif statetype == 2:
            directory = os.path.join(".", "Data", str(year), "Pon")
        else:
            directory = os.path.join(".", "Data", str(year), "Kan")


        os.makedirs(directory, exist_ok=True)
        
        file_path = os.path.join(directory, f"{logid}.npz")
        
        np.savez_compressed(file_path, arr_np)
            



def saveToFile(log, year):

    tupl = convertLog(log)

    game = tupl[1]
    gameid = tupl[0]

    game_riichi = matrixify(game)

    game_chi, game_pon, game_kan = matrixifymelds(game)

    flatformat(game_riichi, gameid, 0, year)
    flatformat(game_chi, gameid, 1 , year)
    flatformat(game_pon, gameid, 2 , year) 
    flatformat(game_kan, gameid, 3 , year)


def saveFilesPerYear(year, numFiles = None):

    dbfile = 'es4p.db'

    con = sqlite3.connect(dbfile)

    cur = con.cursor()

    res = cur.execute(f"SELECT COUNT(*) FROM logs WHERE year = {year}")

    numGames = res.fetchone()[0]

    print(year)

    res = cur.execute(f"SELECT log_id, log_content FROM logs WHERE year = {year}")

    if numFiles:
        numGames = numFiles
        

    for i in tqdm(range(numGames), desc="Processing games"):
        log = res.fetchone()

        try:
            saveToFile(log, year)
        except Exception as e:
            pass
            # print(f"An error occurred with i={i}: {e}")
            # traceback.print_exc()

    con.close()

def saveAll():
    for year in range(2017, 2018):
        #Change this Parameter to change number of games saved per year
        #IMPORTANT - if you don't include this parameter it will save EVERYTHING
        saveFilesPerYear(year)


start_time = time.time()

start_time = time.time()

saveAll()

end_time = time.time()

duration = end_time - start_time

print(f"saveAll() took {duration:.4f} seconds")
