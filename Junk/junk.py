def decodeMeld(data):
    def decodeChi(data):
        meldType = 0
        t0, t1, t2 = (data >> 3) & 0x3, (data >> 5) & 0x3, (data >> 7) & 0x3
        baseAndCalled = data >> 10
        called = baseAndCalled % 3
        base = baseAndCalled // 3
        base = (base // 7) * 9 + base % 7
        tiles = [(t0 + 4 * (base + 0))//4, (t1 + 4 * (base + 1))//4, (t2 + 4 * (base + 2))//4]
        return tiles, meldType

    def decodePon(data):
        t4 = (data >> 5) & 0x3
        t0, t1, t2 = ((1,2,3),(0,2,3),(0,1,3),(0,1,2))[t4]
        baseAndCalled = data >> 9
        called = baseAndCalled % 3
        base = baseAndCalled // 3
        if data & 0x8:
            meldType = 1
            tiles = [(t0 + 4 * base)//4, (t1 + 4 * base)//4, (t2 + 4 * base)//4]
        else:
            meldType = 4
            tiles = [(t0 + 4 * base)//4, (t1 + 4 * base)//4, (t2 + 4 * base)//4]
        return tiles, meldType

    def decodeKan(data, fromPlayer):
        baseAndCalled = data >> 8
        if fromPlayer:
            called = baseAndCalled % 4
        base = baseAndCalled // 4
        meldType = 2
        tiles = [base, base, base, base]
        return tiles, meldType

    data = int(data)
    meld = data & 0x3
    if data & 0x4:
        meld = decodeChi(data)
    elif data & 0x18:
        meld = decodePon(data)
    elif data & 0x20:
        meld = decodeNuki(data)
    else:
        meld = decodeKan(data, False)
    return meld                       #chi:0, pon:1, openKan:2, closedKain:3, chakan:4



def canChi(hand, tile): # need to write logic to check for seat (can only chi from person before you)
        if tile//9 == 3: return False
        else:
            t = tile % 9
            h = hand
            # skull
            if t == 0: return (h[tile+1]>0 and h[tile+2]>0)
            elif t == 8: return (h[tile-1]>0 and h[tile-2]>0)
            elif t == 1: return (h[tile+1]>0 and h[tile+2]>0) or (h[tile-1]>0 and h[tile+1]>0)
            elif t == 7: return (h[tile-1]>0 and h[tile-2]>0) or (h[tile-1]>0 and h[tile+1]>0)
            else: return (h[tile-1]>0 and h[tile-2]>0) or (h[tile-1]>0 and h[tile+1]>0) or (h[tile+1]>0 and h[tile+2]>0)


print(canChi([0]*9 + [1,2,2,1,0,1,0,0,0]+[0]*9+[0]*7,9))