#Class used to store all data about the game

from Global import *

from matrix import Matrix


class GameData(Matrix):
    
    #points [1,2,3,4], dealer (0-3), roundWind (0-3) honbaSticks (int)

    def __init__(self, points = [250,250,250,250], dealer = 0, roundWind = 0, honbaSticks = 0, eastOnly = False):
        
        ### Define Variables ###

        with open('tiles.json', 'r') as file:
            start_tiles = json.load(file)

        self.eastOnly = eastOnly

        self.playerTurn = dealer 
        self.turnNumber = 1

        #self.orderedMelds = [[([5,6,7],1) , ([5,5,5],1) , [] ],[],[],[]]
        self.orderedMelds = [[],[],[],[]]

        #self.orderedPool = [[1,2,4,6],[],[],[]]
        self.orderedPool = [[],[],[],[]]

        self.orderedDora = []

        super().__init__()

        ### Initialise Game ###

        self.tilePool = start_tiles
            
        initialHands = [self.convertHandFormat([self.getRandTile() for i in range(13)]) for j in range(4)]
        
        #sets points
        self.setPlayerScore(points)
        
        #sets player winds
        self.setDealer(dealer)
        self.setPlayerWinds()

        #sets starting hands
        self.initialisePrivateHands(initialHands)

        #sets more metadata form seed
        
        self.setHonbaSticks(honbaSticks)
        self.setRoundWind(roundWind)
        self.newDora()


        
    def incPlayerTurn(self):
        
        self.playerTurn = (self.playerTurn + 1) % 4

    def setPlayerTurn(self, playerTurn):
        self.playerTurn = playerTurn
    
    def convertHandFormat(self, hand):
        newHand = [0] * 34
        for tile in hand:
            newHand[tile] += 1
        
        return newHand


    def getRandTile(self):
        keys, weights = zip(*self.tilePool.items())

        if any(weights):
            tempRandomElement = random.choices(keys, weights=weights)[0]
            self.tilePool[tempRandomElement] -= 1
            return int(tempRandomElement)
        
        else:
            return None

    def getNumKans(self):
        sum(self.kansNum)

    def newDora(self):
        dora = self.getRandTile()
        self.addDoraIndicator(dora)

    def incTurnNumber(self):
        self.turnNumber +=1

    ### Overriden Methods ### 

    def addPlayerPool(self, player, tile):
        self.playerPool[player][tile] += 1
        self.orderedPool[player].append(tile)
    
    def decPlayerPool(self, player, tile):
        self.playerPool[player][tile] -= 1
        self.orderedPool[player].remove(tile)

    def addDoraIndicator(self, doraIndicator):
        self.orderedDora.append(doraIndicator)
        super().addDoraIndicator(doraIndicator)


    def printGood(self, player, file):
        self.buildMatrix(player)
        print(file=file)
        printNice(self.gameState,file=file)
        print(f"Shanten: {self.totalHandShanten(player)}",file=file)
        print(file=file)

    def __str__(self):

        # self.buildMatrix(0)
        # printNice(self.gameState)
        print("")
        print(self.privateHands)
        print("")

        return ""
    
    def get_all_attributes(self):
        attributes = {}
        current_class = self.__class__
        
        # Traverse through the MRO (Method Resolution Order)
        for cls in current_class.__mro__:
            if cls == object:
                continue  # Skip the base 'object' class
            # Get instance attributes if the current object is an instance of the class
            if '__dict__' in cls.__dict__:
                attributes.update(self.__dict__)

        # Format attributes manually
        def format_value(value):
            if isinstance(value, np.ndarray):
                if value.ndim == 1:
                    return '[' + ', '.join(map(str, value.tolist())) + ']'
                elif value.ndim == 2:
                    return '[\n ' + ',\n '.join(['[' + ', '.join(map(str, row.tolist())) + ']' for row in value]) + '\n]'
            return repr(value)

        formatted_attributes = []
        for key, value in attributes.items():
            formatted_attributes.append(f'    "{key}": {format_value(value)}')

        formatted_string = "{\n" + ",\n".join(formatted_attributes) + "\n}"
        return f'{self.__class__.__name__}:\n{formatted_string}'
    
        # calculates actual shanten on the player (melds mess this up)
    def totalHandShanten(self, player):
        hand = self.privateHands[player]
        numCalledMelds = self.getMeldNum(player)

        return calcShanten( hand=hand, numCalledMelds=numCalledMelds)
    
    
    #meldType 0-Chi, 1-Pon, 2-Kon, 3-Closedkan, 4-Chakan

    #ordered Meld Type (Tile, meldType (0-chi, 1-Pon, 2-kan, 3-closedkan))
    def handleMeld(self, player, meldInfo, fromPlayer = None):
        meldTiles = meldInfo[0] #tiles in ascending order
        meldType = meldInfo[1]

        # (ordering of if and elif is important here)
        # handles chakan
        if meldType == 4: 

            self.decPlayerPonTiles(player, meldTiles)
            self.decPon(player)
            self.playerMelds[player][ meldTiles[0] ] = 4
            self.orderedMelds[player].append((meldTiles[0], 1)) #remove pon
            self.orderedMelds[player].append((meldTiles[0], 2)) #add kan
            self.addKan(player)
            self.privateHands[player][ meldTiles[0]] = 0
       
        # handles closed kan       
        elif meldType == 3: 
            self.privateHands[player][ meldTiles[0]] = 0
            self.addKan(player)
            self.playerMelds[player][ meldTiles[0]] = 4
            self.orderedMelds[player].append((meldTiles[0], meldType))

        # handles regular call
        else:
        
            lastDiscard = self.lastDiscardTile
            self.setOpen(player)
            # adds meld tiles to meld attribute
            self.orderedMelds[player].append((meldTiles[0], meldType))
            self.decPlayerPool(fromPlayer, lastDiscard) 

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
