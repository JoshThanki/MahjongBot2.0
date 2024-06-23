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