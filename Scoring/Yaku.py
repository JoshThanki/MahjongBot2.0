import numpy as np
from gameData import GameData
import SplitHand

#gameData, player, typeWin, tile

# ONE HAN CLOSED ONLY

hand = []
trips = []
seqs = []
pair = 0
elements = [[0, 1, 2, 3, 4, 5, 6, 7, 8], [9, 10, 11, 12, 13, 14, 15, 16, 17], [18, 19, 20, 21, 22, 23, 24, 25, 26]]


def getHand(gameData, player, typeWin):
    hand = SplitHand.findWinningHandSplits(gameData, player, typeWin)
    for i in range(0, 4):
        if hand[i][0] == hand[i][1]:
            trips.append(hand[i])
        else:
            seqs.append(hand[i])
    pair = hand[4]


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
        
        tuples = [tuple(trip) for trip in trips]

        count_set = {}
        duplicate_array = []

        for t in tuples:
            if t in count_set:
                count_set.remove(t)
                duplicate_array.append(t)  # Save the duplicate array
            else:
                count_set.add(t)

        if len(count_set) > 0:
            return len(count_set)
        

# ONE HAN

def Haitei_raoyue(gameData, typeWin):
    if (gameData.wallTiles == 0 and typeWin == 3):
        return 1

def Houtei_raoyui(gameData, typeWin):
    if (gameData.wallTiles == 0 and typeWin == 2):
        return 1

# def Rinshan_kaihou (will ignore)
# def Chankan (will ignore)

def Tanyao():
    for i in range (0, 5):
        if hand[i][0] == 1 or hand[i][-1] == 9:
            return 0
    return 1

def Yakuhai(gameData, player):
    target_numbers = {31, 32, 33}
    target_numbers.add(gameData.roundWind + 27)
    target_numbers.add(gameData.playerWinds[player] + 27)

    temp = 0
    for i in range (0, len(trips)):
        if trips[i][0] in range(31, 34):
            if gameData.roundWind == gameData.playerWinds[player]:
                temp += 2
            else:
                temp += 1
    if temp > 0:
        return temp

# TWO HAN

# def Double_riichi (will do)

def Chintaiyao(gameData, player):
    target_numbers = {0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33}
    check = True

    for i in range (0, 5):
        if hand[i][0] not in target_numbers or hand[i][-1] not in target_numbers:
            check = False
            break
    
    if check == True:
        if gameData.getClosed[player] > 0:
            return 2
        else:
            return 1

def Sanshoku_doujun(gameData, player):
    if len(seqs) > 2:
        count_set = {}
        count = 0
        for seq in seqs:
            # convert each sequence to its normalised format (1-9) as a tuple so it can be compared within a set
            norm_set = tuple(sorted(((tile % 9) + 1) for tile in seq)) 
            
            # Calculate whether the given sequence is of man (0-8), pin (9-17) or sou (18-26)
            set_index = None
            if 0 <= seq[0] <= 8:
                set_index = 0
            elif 10 <= seq[0] <= 17:
                set_index = 1
            elif 18 <= seq[0] <= 26:
                set_index = 2

            if set_index is None:
                continue

            # Check if the normalized group is already in the dictionary
            if norm_set not in count_set:
                count_set[norm_set] = set()
            
            # Add the set index to the set of this normalized group
            count_set[norm_set].add(set_index)
            
            # If there are at least 3 different sets for the same normalized group return some han
            if len(count_set[norm_set]) >= 3:
                if gameData.getClosed[player] > 0:
                    return 2
                else:
                    return 1


def Ittsu(gameData, player):
    if len(seqs) > 2:
        set_seqs = {0: set(), 1: set(), 2: set()}
    
        # Iterate through each group (sequence of 3 tiles)
        for group in seqs:
            # Normalize the group
            normalized_seqs = {normalize_tile(tile) for tile in group}
            
            # Determine the set index
            if 0 <= group[0] <= 8:
                set_index = 0
            elif 10 <= group[0] <= 17:
                set_index = 1
            elif 18 <= group[0] <= 26:
                set_index = 2
            else:
                continue
            
            # Add normalized values to the corresponding set index
            set_seqs[set_index].update(normalized_seqs)
        
        # Check if any set contains all numbers from 1 to 9
        for key in set_seqs:
            if set_seqs[key] == set(range(1, 10)):
                if gameData.getClosed[player] > 0:
                    return 2
                else:
                    return 1
        
        return 0
    
def Toitoi(gameData, player):
    if len(trips) == 4:
        return 1

def Sanankou_or_doukou(gameData, player):
    if len(trips) == 3 and len(gameData.getPlayerPonTiles(player)) == 0:
        for i in range (0, 1):
            if ((trips[i] % 9) + 1) != ((trips[i+1] % 9) + 1):
                return 2
        return 4


def Sankantsu(gameData, player):
    if gameData.get

# def chitoitsu (will do)

def Honroutou(gameData, player):
    if len(trips) == 4:
        target_numbers = {0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33}

        if pair in target_numbers:
            for trip in trips:
                if trip[0] not in target_numbers:
                    return 0
            return 2
        
def Shousangen(gameData, player):
    target_numbers = {31, 32, 33}
    if len(trips) > 1 and pair in target_numbers:
        target_numbers.remove(pair)
        for trip in trips:
            if trip[0] in target_numbers:
                target_numbers.remove(trip[0])
            if len(target_numbers) == 0:
                return 2
            

# THREE HAN 

def Honitsu(gameData, player):
    sets = trips + seqs
    for set_i in elements:
        if sets[0][0] in set_i:
            check = set(set_i)
            check.update({27, 28, 29, 30, 31, 32, 33})
            break
    for grp in sets:
        for tile in grp:
            if tile not in check:
                return 0
    if pair not in check:
        return 0
    else:
        if gameData.getClosed[player] > 0:
            return 3
        else:
            return 2
        
def Junchan_taiyao(gameData, player):
    if (pair % 9) not in {0, 8}:
        return 0
    else:
        sets = trips + seqs
        for i in sets:
            if i[0] % 9 not in {0, 8}:
                return 0
        if gameData.getClosed[player] > 0:
            return 3
        else:
            return 2
        
# SIX HAN

def Chinitsu(gameData, player):
    for i in elements:
        if pair in i:
            check = set(i)
            break
    sets = trips + seqs
    for i in sets:
        if i[0] not in check:
            return 0
    if gameData.getClosed[player] > 0:
        return 6
    else:
        return 5
    
# YAKUMAN

def Kokushi_musou(gameData, player):
    target_tiles = {0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33}
    # Will complete

def Suuankou(gameData, player, typeWin):
    if typeWin == 3 and len(trips) == 4:
        return 12
    
def Daisangen():
    if len(trips) < 3:
        return 0
    else:
        count = 0
        for trip in trips:
            if trip[0] in range(31, 34):
                count += 1
        if count == 3:
            return 12
        else:
            return 0
        
def Shousuushii():
    target_tiles = {27, 28, 29, 30}
    if pair not in target_tiles or len(trips) < 3:
        return 0
    else:
        target_tiles.remove(pair)
        for trip in trips:
            if trip[0] in target_tiles:
                target_tiles.remove(trip[0])
        if len(target_tiles) == 0:
            return 12
        else:
            return 0
        
def Daisuushii():
    if len(trips) == 4:
        target_tiles = {27, 28, 29, 30}
        for trip in trips:
            if trip[0] not in target_tiles:
                return 0
        return 12
    else:
        return 0
    
def Tsuuiisou():
    

        

        


        


                




