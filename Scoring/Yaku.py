import numpy as np
from gameData import GameData
import checkYaku 

#gameData, player, typeWin, tile

yakus = {}

# ONE HAN CLOSED ONLY







def Menzenchin_tsumohou(gameData, player, typeWin):
    if (typeWin==3) and (gameData.getClosed(player)):
        return 1

def Riichi(gameData, player):
    if gameData.getRiichi(player):
        return 1

#def Ippatsu(gameData, player):
    # Will do


def Pinfu(gameData, player, typeWin):
    if gameData.getClosed(player) and getFu(split)==20:######
        return 1
        


def Iipeikou(gameData, player):
    if (gameData.getClosed(player)):
        hand = checkYaku.checkYaku(gameData.privateHands[player])
        
        tuples = [tuple(trip) for trip in hand]

        count_set = {}
        duplicate_array = []

        for t in tuples:
            if t in count_set:
                count_set.remove(t)
                duplicate_array.append(t)  # Save the duplicate array
            else:
                count_set.add(t)

        if len(count_set) > 0:
            yakus[4] = len(count_set)
        

# ONE HAN

def Haitei_raoyue_Houtei_raoyui(gameData, typeWin):
    if (gameData.wallTiles == 0):
        if(typeWin == 3):
            yakus[5] = 1
        elif(typeWin == 2):
            yakus[6] = 1

# def Rinshan_kaihou (will do)
# def Chankan (will do)

def Tanyao(gameData, player):
    hand = checkYaku.checkYaku(gameData.privateHands[player])

    for i in range (0, 5):
        if hand[i][0] != 1 and hand[i][len(hand[i]) - 1] != 9:
            yakus[9] = 1

def Yakuhai(gameData, player):
    trips = checkYaku.getTriplets(player)
    temp = 0
    for i in range (0, len(trips)):
        if trips[i][0] in range(31, 34):
            temp += 1
    if temp > 0:
        yakus[10] = temp

# TWO HAN

# def Double_riichi (will do)

def Chintaiyao(gameData, player):
    hand = checkYaku.checkYaku(gameData.privateHands[player])
    target_numbers = {0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33}
    check = True

    for i in range (0, 5):
        if hand[i][0] not in target_numbers and hand[i][len(hand[i]) - 1] not in target_numbers:
            check = False
            break
    
    if check == True:
        yakus[12] = 1

def Sanshoku_doujun(gameData, player):
    seqs = checkYaku.getSequences(player)
    if len(seqs) > 2:
        # Will complete

# def Ittsu (will do)
    
def Toitoi(gameData, player):
    if len(checkYaku.getTriplets(player)) == 4:
        yakus[15] = 1

def Sanankou_or_doukou(gameData, player):
    trips = checkYaku.getPrivSets(player)
    if len(trips) >= 3:
        for trip in trips:
            # will complete

def Sankantsu(gameData, player):
    sets = checkYaku.getPrivSets(player)
    if len(sets) >= 3:
        yakus[18] = 1
        for set in sets:
            if len(set) != 4:
                del yakus[18]
                break

# def chitoitsu (will do)


                




