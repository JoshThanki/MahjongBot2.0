from imports import *

from data import X_test, y_test

#pulling model
model = tf.keras.models.load_model('D:\BOT TRAINING')

#testing
results = model.evaluate(X_test, y_test)
print(f'Test Loss: {results[0]}')
print(f'Test Accuracy: {results[1]}')