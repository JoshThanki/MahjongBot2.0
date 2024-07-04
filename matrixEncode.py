
#global functions
from Global import *

from matrix import Matrix


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

            isPonInPriotity = lambda player:  (isNextCallPon or isNextCallKan) and (player != callPlayer)
       
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
    
    #make sure that states are non empty, before saving to file
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
        saveFilesPerYear(year, 500)


start_time = time.time()

start_time = time.time()

saveAll()

end_time = time.time()

duration = end_time - start_time

print(f"saveAll() took {duration:.4f} seconds")
