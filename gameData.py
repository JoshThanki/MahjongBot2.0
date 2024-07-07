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
        self.orderedPool[player].pop(tile)

    def addDoraIndicator(self, doraIndicator):
        self.orderedDora.append(doraIndicator)
        super().addDoraIndicator(doraIndicator)


    def __str__(self):
        return self.get_all_attributes()
    
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
    
    def handleMeld(self, player, meldInfo, isClosedCall=False, fromPlayer = None):
        meldTiles = meldInfo[0]
        meldType = meldInfo[1]

        # (ordering of if and elif is important here)
        # handles chakan
        if meldType == 3: 
            self.decPlayerPonTiles(player, meldTiles)
            self.decPon(player)
            self.playerMelds[player][ meldTiles[0] ] = 4
            self.orderedMelds[player].pop(([meldTiles[0]*3],1))
            self.orderedMelds[player].add(([meldTiles[0]*4],1))
            self.addKan(player)
            self.privateHands[player][ meldTiles[0] ] = 0
       
        # handles closed kan       
        elif isClosedCall:
            self.privateHands[player][ meldTiles[0] ] = 0
            self.addKan(player)
            self.playerMelds[player][ meldTiles[0] ] = 4
            self.orderedMelds[player].add(([meldTiles[0]*4],0))

        # handles regular call
        else:
            lastDiscard = self.lastDiscardTile
            self.setOpen(player)
            # adds meld tiles to meld attribute
            self.orderedMelds[player].add(meldTiles)
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
