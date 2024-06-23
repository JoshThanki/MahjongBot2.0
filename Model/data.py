from imports import *

# num of games for
num_train = 1     #training
num_test=1        #testing 
num_validate=500  #validating (used in training)


#converting label to one-hot format for training
def one_hot(array):
    out = np.zeros((array.size, 34))
    out[np.arange(array.size), array] = 1
    return out


#defining file paths (for my pc)
discard_dataset_path = "D://Mahjong group project data/archive/discard_datasets"
dataset_folder_train = Path(discard_dataset_path) / "2015" 
dataset_folder_test = Path(discard_dataset_path) / "2014" 
dataset_folder_validate = Path(discard_dataset_path) / "2013" 

#pulling files
files_train = list(dataset_folder_train.iterdir())[:num_train]
files_test = list(dataset_folder_test.iterdir())[:num_test]
files_validate = list(dataset_folder_validate.iterdir())[:num_validate]

#pulling data from files
matrix_train = np.vstack([sp.load_npz(npz_file).toarray() for npz_file in tqdm(files_train)])
matrix_test = np.vstack([sp.load_npz(npz_file).toarray() for npz_file in tqdm(files_test)])
matrix_validate = np.vstack([sp.load_npz(npz_file).toarray() for npz_file in tqdm(files_validate)])

#formatting data (X are states and y are labels)
X_train = matrix_train[:, :510]
y_train = one_hot( matrix_train[:, -1] )
X_test = matrix_test[:, :510]
y_test = one_hot( matrix_test[:, -1] )
X_validate = matrix_validate[:, :510]
y_validate = one_hot( matrix_validate[:, -1] )