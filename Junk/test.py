import tensorflow as tf


data = [[0]*374]

model = tf.keras.models.load_model('Saved Models\discardModel')
#gameData.buildMatrix(player)
prediction = model( data )

print(prediction)