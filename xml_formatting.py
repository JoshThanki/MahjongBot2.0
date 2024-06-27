import numpy as np

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

# the superior tile dictionary (PLEASE USE IN xmlFilter)
tile_dic = {i: f"{i+1}_man" if i <= 8 else f"{i-8}_pin" if i <= 17 else f"{i-17}_sou" for i in range(27)}
honour_entries = {27 : "East", 28 : "South", 29 : "West", 30 : "North", 31 : "White", 32 : "Green", 33 : "Red"}
tile_dic.update(honour_entries)

def meldDecode(meld):
    t0, t1, t2 = (meld >> 3) & 0x3, (meld >> 5) & 0x3, (meld >> 7) & 0x3

    baseAndCalled = meld >> 10
    base = baseAndCalled // 3
    base = (base // 7) * 9 + base % 7

    meldTiles = [t0 + 4*(base + 0), t1 + 4*(base + 1), t2 + 4*(base + 2)]
    return base, tile_dic[base], meldTiles

def decodeList(list, dtype = int):
    return tuple(dtype(i) for i in list.split(","))

seed = "0,0,0,5,2,46"

print( seed.split(",") )