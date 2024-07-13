from Global import *
from gameData import GameData
from action import Action

from pathlib import Path
import tensorflow as tf
import keras


def convertModel(path):
    model = tf.keras.models.load_model(path)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_quant_model = converter.convert()

    # Save the quantized model
    with open('model_quant.tflite', 'wb') as f:
        f.write(tflite_quant_model)