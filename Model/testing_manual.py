# I used this for manually looking at games

from MLimports import *
np.set_printoptions(formatter={'float': '{:0.8f}'.format})

# defining dictionary containing each tile and its index
tile_dictionary = {i: f"{i+1}_man" if i <= 8 else f"{i-8}_pin" if i <= 17 else f"{i-17}_sou" for i in range(27)}
honour_entries = {27 : "East", 28 : "South", 29 : "West", 30 : "North", 31 : "White", 32 : "Green", 33 : "Red"}
tile_dictionary.update(honour_entries)

# formatting label (one-hot) to the tile
def format_label(y):
    index = np.argmax(y)
    return tile_dictionary[index]

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

# formatting prediction of the model to a readable format
def format_prediction(array):
    return {tile_dictionary[i]: array[i].numpy() for i in range(34)}


from data import X_test, y_test
model = tf.keras.models.load_model('D:\BOT TRAINING')
predictions = model(X_test)


num=131
predictions_dict = format_prediction(predictions[num])
predictions_dict_sorted = {k: v for k, v in sorted(predictions_dict.items(), key=lambda item: item[1], reverse=True)}

print(f'hand: {webFormat(X_test[num][68:102])}')
print('')
print(f'prediction: {predictions_dict}')
print('')
print(f'prediction_sorted: {predictions_dict_sorted}')
print('')
print(f"actual tile discard: {format_label(y_test[num])}")



#test= [0,1,0,1,1,0,2,0,0,0,1,0,1,1,0,2,0,0,0,1,0,1,1,0,2,0,0,2,0,0,0,0,0,0]
#pred = format_prediction(test)
#sorte = {k: v for k, v in sorted(pred.items(), key=lambda item: item[1], reverse=True)}
#print(webFormat(test))
#print(pred)
#print(sorte)
