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


    # meldInfo:  (tiles in meld (0-3),  meldType)
    # meldType: 0-chi, 1-pon, 2-kan, 3-chakan
def addPlayerMelds(self, player, meldinfo, isClosedKan):
    meldTiles = meldinfo[0]
    # adds the meld to the playerMeld attribute
    for tile in meldTiles:
        self.playerMelds[player][tile] += 1 

    # it doesnt get called from other player so special handling
    if isClosedKan:
        tile = meldTiles[0]
        self.privateHands[player][tile] -= 4 
    else:
        called = self.lastDiscardTile
        meldTiles.remove(called)  
        for tile in meldTiles:
            self.privateHands[player][tile] -= 1

    meldType = meldinfo[1]
    #if pon
    if meldType == 1:
        self.addPlayerPonTiles(player, meldTiles)

    ### CHAKAN ### 
    elif meldType == 3:
        #removes pon
        self.decPlayerPonTiles(player, meldTiles)
        self.decPon(player)
        self.playerMelds[player][ meldTiles[0] ] -= 2
        #adds kan number
        self.addKan(player)
        #adds tiles back into player
        self.privateHands[player][ meldTiles[0] ] += 3

