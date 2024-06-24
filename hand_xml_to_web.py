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

def format_xmlHand(string):
    out=np.zeros(34, dtype=int)
    string_list = string.split(",")
    array = np.array([int(i) for i in string_list])
    for i in array:
        out[i // 4] +=1
    return webFormat(out)



def first6bits(num):
    # Step 1: Convert integer to 16-bit binary
    binary_representation = format(num, '016b')  # '016b' ensures 16-bit binary representation

    #print(binary_representation)
    # Step 2: Extract first 6 bits
    first_6_bits = binary_representation[:6]

    # Step 3: Convert binary to decimal (base-10)
    decimal_value = int(first_6_bits, 2)

    return decimal_value

#36,42,47

Base=36/4
i=0

print(36 - 4 * i - Base * 4)


print(first6bits(24007)%3)

def decodeMeld(meld):
    binary_meld = format(meld, '016b')
    chi = binary



#Base = 36/4
#print(((Base / 9) * 7 + Base % 9) * 3 + 2)