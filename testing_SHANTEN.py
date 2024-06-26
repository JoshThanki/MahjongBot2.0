import numpy as np
import time
from tqdm import tqdm

# webFormat from mahjong 1.0, we represented hands slightly differently in that project so this function is slightly distinct
def webFormat_10(handArray):
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


def calcShanten(handArray):

    out = np.zeros(34, dtype=int)
    string_list = handArray.split(",")
    handArray = np.array([int(i) for i in string_list])
    for i in handArray:
        out[i // 4] +=1
    
    #converting to mahjong 1.0 format
    split_indices=[9,18,27]
    handArray =  np.split(out, split_indices) 

    def pairs(suit_arr):
        possible_pairs=[]

        for i in range(9):
            if suit_arr[i]>1:
                out = [0]*9
                out[i] = 2
                possible_pairs.append(out)
        return possible_pairs
    
    def triplets(suit_arr):
        possible_triplets=[]

        for i in range(9):
            if suit_arr[i]>2:
                out = [0]*9
                out[i] = 3
                possible_triplets.append(out)
        return possible_triplets
    
    def complete_sequences(suit_arr):
        possible_sequences=[]
        for i in range(2,9):
            if suit_arr[i]>0 and suit_arr[i-1]>0 and suit_arr[i-2]>0:
                out = [0]*9
                out[i]=1
                out[i-1]=1
                out[i-2]=1
                possible_sequences.append(out)
        return possible_sequences
    
    def incomplete_sequences(suit_arr):
        possible_insequences=[]
        if suit_arr[0]>0 and suit_arr[1]>0:
            out = [0]*9
            out[0]=1
            out[1]=1
            possible_insequences.append(out)
        for i in range(2,9):
            if suit_arr[i]>0 and suit_arr[i-1]>0:
                out = [0]*9
                out[i]=1
                out[i-1]=1
                possible_insequences.append(out)
            if suit_arr[i]>0 and suit_arr[i-2]>0:
                out = [0]*9
                out[i]=1
                out[i-2]=1
                possible_insequences.append(out)
        return possible_insequences
    
    def resulting_hand(arr1,arr2):
        out=[0]*9
        for i in range(9):
            out[i] = arr1[i] - arr2[i]
        return out
    

    def splits_nogroups(hand):
        set_insequences = incomplete_sequences(hand)
        current_shan=0
        set_pairs = pairs(hand)
        pair_bool = False

        for i in set_pairs:
            current = splits_nogroups(resulting_hand(hand, i))[0]+1
            if current>current_shan:
                current_shan = current
                pair_bool = True

        for i in set_insequences:
            current = splits_nogroups(resulting_hand(hand, i))[0]+1
            if current > current_shan:
                current_shan = current
                pair_bool = splits_nogroups(resulting_hand(hand, i))[1]

        return current_shan, pair_bool


    def splits(g, hand):                  #******
        current_g_n = g                   #number of groups
        current_i_n = 0                   #number of taatsu
        pair_presance = False             #used for an edge case(s?)                            
        set_seq = complete_sequences(hand)
        set_triplets = triplets(hand)

        for j in set_seq:
            current_split = splits(g+1, resulting_hand(hand,j))   
            current = current_split[0]
            if current>current_g_n:
                current_g_n = current
                current_i_n = current_split[1]
                pair_presance = current_split[2]   #*
            elif current == current_g_n:
                if current_split[1] > current_i_n:
                    current_i_n = current_split[1]
                    pair_presance = current_split[2]   #*

        for j in set_triplets:
            current_split = splits(g+1, resulting_hand(hand,j))
            current = current_split[0]
            if current>current_g_n:
                current_g_n = current
                current_i_n = current_split[1]
                pair_presance = current_split[2]   #*
            elif current == current_g_n:
                if current_split[1] > current_i_n:
                    current_i_n = current_split[1]
                    pair_presance = current_split[2]   #*
                    
        if (not set_seq) and (not set_triplets):     #if no more groups then counts maximum of taatsu    
            s=splits_nogroups(hand)
            return g, s[0], s[1]

        return current_g_n,current_i_n,pair_presance
    

    def splits_fullhand(hand):
        current_split = [0,0,False]
        for i in hand[:3]:
            current_arr = splits(0, i)
            current_split[0] += current_arr[0]
            current_split[1] += current_arr[1]
            if current_arr[2] == True:
                current_split[2] = True

        for i in hand[3]:
            if i == 3:
                current_split[0] += 1
            elif i == 2:
                current_split[1] +=1
                current_split[2] = True
        return current_split


    def general_shanten(handArray):
        split_arr = splits_fullhand(handArray)
        i = split_arr[1]
        g = split_arr[0]
        pair_presence = split_arr[2]
        p=0

        #checking for the edge cases:
        if i >= 5-g and pair_presence == False:
            p=1
        return 8 - 2*g - min(i, 4-g) - min(1, max(0,i+g-4)) + p

    
    def chiitoistu_shanten(handArray):
        pairs = 0
        for suit in handArray:
            for num in suit:
                pairs += num//2      #counts number of pairs, 4 of the same tile are treated as 2 pairs
        return 6 - pairs
    
    def orphanSource_shanten(handArray):
        diffTerminals = 0
        pairsTerminals = 0
        pair_const = 0
        for i in (0,8):                  #iterates over numbered suits
            for suit in handArray[:3]:
                pairsTerminals += min(1, suit[i]//2)
                diffTerminals += min(1, suit[i]//1)


        for num in handArray[3]:        #iterates over honours
                pairsTerminals += min(1, num//2)
                diffTerminals += min(1, num//1)
        if pairsTerminals > 0:
            pair_const=1
        return 13 - diffTerminals - pair_const

    
    return min(general_shanten(handArray), chiitoistu_shanten(handArray), orphanSource_shanten(handArray))

def format_xmlHand(string):
    if string == "":
        return ""
    out=np.zeros(34, dtype=int)
    string_list = string.split(",")
    array = np.array([int(i) for i in string_list])
    for i in array:
        out[i // 4] +=1
    return out



#testing speed
start_time = time.time()
for i in tqdm(range(10)):
    hand = "34,27,20,47,130,98,132,102,13,133,2,79,31"
    #hand = format_xmlHand(hand)
    #webFormat0(hand)
    calcShanten(hand)
end_time = time.time()
print(calcShanten(hand))
#print(webFormat_10(hand))
print(end_time-start_time)
