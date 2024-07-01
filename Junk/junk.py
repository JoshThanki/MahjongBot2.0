import numpy as np
np.set_printoptions(threshold=np.inf, linewidth=np.inf)
import scipy.sparse as sp
from pathlib import Path
import os
from tqdm import tqdm

def one_hot(array):
    out = np.zeros((array.size, 34))
    out[np.arange(array.size), array] = 1
    return out

discard_dataset_path = "Data"
dataset_folder_train = Path(discard_dataset_path) / "2020"

file_list = list(dataset_folder_train.glob('0*'))

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

            print(mats)
            print()
            print(labels)

            exit()

        
def load_npz_file(file):
    try:
        loaded_data = np.load(file)
        # Initialize lists to store matrices and labels
        matrices = []
        labels = []
        
        # Iterate over keys in the npz file
        data = loaded_data["arr_0"]

        for arr in data:

            matrix = arr[:-1]
            label = arr[-1] 
            
            matrices.append(matrix)
            labels.append(label)


        return np.array(matrices), np.array(labels)
    
    except Exception as e:
        print(f"Error loading {file}: {e}")
        return None, None
    
#npzfiles(file_list)

a = [0,1,2,3,4]

for i in a if i != 0:
    print(i)