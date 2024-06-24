import numpy as np
np.set_printoptions(threshold=np.inf, linewidth=np.inf)
import scipy.sparse as sp
from pathlib import Path
import keras
from keras.models import Model
from keras.layers import Input, Dense, MultiHeadAttention, Flatten, LeakyReLU
from keras.optimizers import SGD
from keras.metrics import categorical_crossentropy
import os
from tqdm import tqdm
import tensorflow as tf

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



def create_dataset(file_paths, batch_size):
    matrix = np.vstack([sp.load_npz(npz_file).toarray() for npz_file in tqdm(file_paths)])
    X_train = matrix[:, :510]
    y_train = matrix[:, -1]

    dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train))    
    dataset = dataset.batch(batch_size)
    dataset = dataset.prefetch(buffer_size=tf.data.experimental.AUTOTUNE)

    return dataset



files_train = list(dataset_folder_train.iterdir())[:100]
batch_size = 10

dataset = create_dataset(file_paths, batch_size)















discard_dataset_path = "D://Mahjong group project data/archive/discard_datasets"
dataset_folder_train = Path(discard_dataset_path) / "2015" 

files_train = list(dataset_folder_train.iterdir())[:1]
matrix_train = np.vstack([sp.load_npz(npz_file).toarray() for npz_file in tqdm(files_train)])

X = matrix_train[:, :510]

X_reshaped = X.reshape(-1, 15, 34)
print(X_reshaped[:10])


#print([webFormat(x[2]) for x in X_reshaped])









