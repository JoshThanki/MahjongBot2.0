import numpy as np

#gameData, player, typeWin, tile

def riichi(gameData, player):
    return gameData.getRiichi(player)

def Menzenchin_tsumohou(gameData, player, typeWin):
    return (typeWin==3) and (gameData.getClosed(player))


def Pinfu(gameData, player):
    if (gameData.getClosed(player)) and typeWin==1:
        return Fu()==30   #placeholder function
    
    else:
        return Fu()==20



