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

seed = "mt19937ar-sha512-n288-base64,7uVp1j7BF26jYzA0xMIgds2FXzv93PKY8nqglbCJRVqxIdpIY9tDU+a873KHSrx3LsYGIeYba+mC0GGfTpkuOrV4JPY52HlbR/rww1tgYyxpkh6WbzwEQnpP7XqsZdys6oDgNkvgZPiKJ9UGaimA5dkj/ali6eMl3FxIKPmaekH0Zf/3IuvSHTIB1YpkwrL/0tc2ZDeqgkCofqreJ4zC596o/FL31jmodZaWMkxnDFOzEYm5kv66QRMEbXzCsUKEvMnV4qPjyD2OuHKDEebYCwE1z9VvgCLYG4rksYCL3BjW+I8ifroxt1Vk2vy0Xyl+d5xfCEQd3qO+8BNzRPvTU3vol0tvXkF5ikxvBkiYgCe5W/ueiiUsReduvO0OLSpfcXJrDKdvvz8IPmI0tUg5XU7R2EvG2wUb2K9w/moG8ZGjWmIfHGVjKjSdNC3BS/If6eIvW5SaXGgKrQECUchyYJkudvl9MGqGFSLezRL0MmXnxA7vQwedH2bST9YvLuHI3ODAo3cLk2MIIM+gGfJe/hBoSe7Ghj+CkFgCtNCe57wLFeAXRKQSd+U6awVNfoO+wAd6mU0pdG7uNOGjkaObAMCQVarD5HVdpJmdhR9gdqwd4r0PFYJVcjIC6TKLV4tKBSmh2cY68Z3DVaewMbFmqRZVDBOvDYEgzR1e8fwjf4LTSRS4BQw3Ik+8h0c9oWEu/biGW/beh2ICsiVzrD+GzZVwO5Np0n/RX1NJr8glgckdNwaStxzcxGiFsfBgaYP1qvg+ZtFNTQKlguZ/WIkQOcrcWeV0ECVN913bOtyMqdy/7aSECRaJRydqQLVVp0lh3IW4BYX9HOoGP2nHT+uQyXEZCzLCrV+YpeWd83oISiWVffvg4orpaaS4ignGk0wXWjo/8HCtMKnxDhEbf6cuwezFtxaLL+SA1vKo1XZMO+lIEMxwmDL4tFDVu2Yfjuw5O/ZqRfCFsh0eeIyufvxgQye622k4L0dEr66nr0VFYw3sFCI3TLn7sZEmJMlfYes9W8GKp8KnOJxAZxBuJbRV5wMgyfrHT871BqJr0N1htqhuShj5jmB3y76OQlDw1Uieo4Se4Ghbvz+JfiQTld5K+1y7N6irruWl4CkB/Cey0KVdl1RHTYm+afcXMhwVui2dXrEK8NySQppch86Zi/BgxHAL0aOyXYWIos49Wuzl/LPJRIcw5YfxF8ClVSe9JkkIWhxxlw+dAjEdvCUyZy5+Fokkwc64ihFjvtm/buQ7K0Fc1POFmysRjtPTg9EFGtmf65nWpOi/64+sUwp3rogWG1z1P1d+kV4iQVkixitlHCKjKDKfV34aG2oj4Zp52BMrgUosN6MQCvIZyOiixtG3eBIQjK9hBMx843kblTmaH0DiI50OxbRXSEGs2aSDEu7sFV7jirYHboepyjONNJ8arG+FVBRa4AhvSahCxwaYbdUek9lGzSWFVhGE3rJB0UZjoa4iNtr8qFzedyO9t8LnNLq8FGWtDFkyxoyNm06AQ+OHg1qIt7IRsSyVWU1GXXLMntMinBhci5Gz6GFTKoKuQkc01tJ134cG1Mv4bacpkD7nOmpyaoITl4qkNvriJE94AscjKF9ADtpusdzG0ga+rq6NG3cqAoyRGFV704hkiWqFtr3zIvGvVz8sN5iTzAOMSBy7u2Q71qUP+EMURrzVSUrhZevNlmmdE20K1kBXw78zxmnRF1fI2vi0vgTis4a9HpVGGHBN/jDThEca7vJyqsE0Tzxdzzy6aD+KD/v3oLSeep7OD1Raj7dzdyibSk42oBNtFt4nHnurnxjysPXeryIS2dC2NwMUUMISFrKmrZfv5MrPJZWGAqcO7hxZ2knnVTdrYujFAtFwNZePEByh9kZJYrusE1Kkwjjs/iUqteIaoTJwLccCLgEDKFzHVmMD7bW4zK/3JcEl2HScZg2E8ArqfZojqEyL/1R1P6TPdnOhj8jk0CqNiNVTpdHURIVeI6pXuttPLkvKq5OY2K7A95T0YeNYytypQBSPrVfnRBVdV8I381xDfxwN3XGA3Qz1WtYxiqxmmOc1qhNbHS+YnKcos/rRntHbdiF16rbJ+e8+zr9ajD/xBMqpOK5C8JNJYwyz7kGz0Pk62zc+A3N3xxkSbaNeODTwrtfGFP9tKSZOWIhP2jlsPyiDhcCQeVR5FdIwGHalCeR/AedSkW3kLhpcT1Fmz8enxiF3I007Qwntz+FaWlhScZmY9+kZS2TqNgKPGKfutVRykkUP6SrAHMNH+HvxtCUFgXLOtLZLPX6mUEoO1RjlHWqwbk9ahHpH0uRWcv0fGch7m3nZcq8fbIXEvbd267ZZWzPKl8g34XNce9OcVR38ioEfbjNeqbFMDANldt83DbNAjGdHsdWh2HEf+y3UW99reFh/rh6KjoPlhH8qoFtNVih11RvwI3a8bFz5MhNvxtSIR51GaHgVKNPriqPcvr+0ZnDjc/dSbgo8kQh8+y7f5k85aM+cIAOAQ4GRIJXQYflkyJQ5FVPjvPF+82M26nlJuFKFaIgigVpXbGoBay56hztAwwnFqUcUolQv2N7pU8njIPY+yyqkxDp8+rsKkq1qcMatzY6QXbjxQVb4SmlSDKAX3fHMvwr3pgRqXvnaFwCevdnw79Z/k45eDjq8YlZ8v3LYHohAvijZNAyCP8wLRDpAZCnlrzoP7oDkvUh/fHjxoS1ir0GMO7s1NJ2KIR60FWkNDkwGccG0LNHLvjj6fZXw6V6RLhPwMmwjlyQumMtoptHB3VnbUyyiSCcsLHJPG4lSRIEfBVF4tNQk5qoOJPJOOSgRnDFFjfGjpEkqkzDI8U2f28F47ZDViznk2tLtdUAaM5N7NE5zV9/i4Xck4PPoWGDi/QK4rPrf6C7egCVTwiux3IwiDAAIDUGFXuhOVMVH6K2gTo/Lz5Jxhe/e8k6rqPbClqK+7nljJcheSa657zIjA2+fJmoMisQObZavKekjCIZQYE8sijst3KBUuMbS3cYwieiLNm3iCzlSla4TLBMfnMshsw2GWzrfAot2K3HflnlRdzVqp3ovjOFVo1FQFEiGp5dwvHwII2LKGp6WP+omn/76Qrf/g7Z4KF/qy4LfIm0EgkQAYfFzIN0czXvap8AOW4glSDRXyAeRz9Oty66rH8q26XZHIEEh3118OgO3ZyAFq7jxBp6hdK7t4rSul+wVFCWzDsEQ+N3ko1AOIez1sm64vixjSksJZTt9032dwvhZrL6l58EsAcHrhMOxhIwHC0I695qo0avSRcZl0pYg8BcCAk6JZyuO9+GmweaxO9yNhOIc3DpAi3IEoRsClqsJil+m"

name, combo, riichi, d0, d1, dora = decodeList(seed)