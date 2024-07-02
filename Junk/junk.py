import numpy as np
np.set_printoptions(threshold=np.inf, linewidth=np.inf)
import scipy.sparse as sp
from pathlib import Path
import os
from tqdm import tqdm


def printNice(game, file = None):
    int_game = [[int(element) for element in row] for row in game]
    game=int_game
    print("round wind: ", game[0][0], "| dealer: ", game[0][1], "| tilesInWall: ", game[0][5], "| doras: ", webFormat(game[1]), "| roundNum: ", game[0][33], "| honba sticks: ", game[0][3], "| riichi sticks: ", game[0][4],"| scores", game[0][6:10] , file=file )
    print("POV wind: "+ windDict[ game[0][2] ]+ " | POVHand: ", webFormat(game[2]) , file=file )  

    for i in range(4):
        print("player"+str(i)+ "| #chi=", game[0][14+i], "| #pon=", game[0][18+i], "| #kan=", game[0][22+i], "| #isOpen=", game[0][26+i],"| melds: "+webFormat(game[3+i]) , file=file )
    for i in range(4):
        print("player"+str(i)+" pool: ",webFormat(game[7+i]) , file=file)


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

    for k, suit in enumerate(handArray):
        if sum(suit) == 0:
            continue
        for num in range(len(suit)):
            if suit[num] == 0:
                continue
            else:
                string += str(num+1)*suit[num]

        string += dict[k]

    return string


windDict = {
        0 : "E",
        1 : "S",
        2: "W",
        3 : "N"
    }





def one_hot(array):
    out = np.zeros((array.size, 34))
    out[np.arange(array.size), array] = 1
    return out

discard_dataset_path = "Data"
dataset_folder_train = Path(discard_dataset_path) / "2020" / "Riichi"

file_list = [file for file in dataset_folder_train.iterdir() if file.suffix == '.npz']

def npz_generator(file_paths):
    for file in file_paths:
        matrix = sp.load_npz(file).toarray()
        X = matrix[:, :374]
        y = one_hot( matrix[:, -1] )
        for i in range(len(X)):
            yield X[i], y[i]


def npzfiles(file_paths):

    for file in file_paths:
            print(file)
            mats, labels = load_npz_file(file)

            for mat in mats:
                printNice(mat)

            print()
            print(labels)

            exit()

        
def load_npz_file(file):
    try:
        loaded_data = np.load(file, allow_pickle=True)
        # Initialize lists to store matrices and labels
        matrices = []
        labels = []
        
        # Iterate over keys in the npz file
        data = loaded_data["arr_0"]

        for arr in data:

            matrix = arr[:-1]

            label = arr[-1] 

            matrix = matrix.reshape(11,34)

            matrices.append(matrix)
            labels.append(label)


        return np.array(matrices), np.array(labels)
    
    except Exception as e:
        print(f"Error loading {file}: {e}")
        return None, None
    
npzfiles(file_list)


