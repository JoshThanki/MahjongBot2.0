from imports import *


gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print("GPUs detected:")
    for gpu in gpus:
        print(f"  - {gpu.name}")
else:
    print("No GPUs detected.")

batch_size = 10000
num_train = 10
num_validate=100


gpus = tf.config.list_physical_devices('GPU')
if gpus: 
    tf.config.set_logical_device_configuration(
        gpus[0],
        [tf.config.LogicalDeviceConfiguration(memory_limit=6000)]
    )
logical_gpus = tf.config.list_logical_devices('GPU')
print(len(gpus), "Physical GPU,", len(logical_gpus), "Logical GPUs")

def one_hot(array):
    out = np.zeros((array.size, 34))
    out[np.arange(array.size), array] = 1
    return out

discard_dataset_path = "D://Mahjong group project data/archive/discard_datasets"
dataset_folder_train = Path(discard_dataset_path) / "2015"
file_list = list(dataset_folder_train.iterdir())[:num_train]

def npz_generator(file_paths):
    for file in file_paths:
        matrix = sp.load_npz(file).toarray()
        X = matrix[:, :510]
        y = one_hot( matrix[:, -1] )
        for i in range(len(X)):
            yield X[i], y[i]



dataset = tf.data.Dataset.from_generator(
    lambda: npz_generator(file_list),
    output_signature=(
        tf.TensorSpec(shape=(510,), dtype=tf.float32),  # Adjust the shape and dtype according to your data
        tf.TensorSpec(shape=(34), dtype=tf.int32)         # Adjust the shape and dtype according to your labels
    )
)
batch_size = 32
dataset = dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)



dataset_folder_validate = Path(discard_dataset_path) / "2014"
files_validate = list(dataset_folder_validate.iterdir())[:num_validate]
matrix_validate = np.vstack([sp.load_npz(npz_file).toarray() for npz_file in files_validate])
X_validate = matrix_validate[:, :510]
y_validate = one_hot( matrix_validate[:, -1] )




input_layer = Input(shape=(510, 1))

attention_output = MultiHeadAttention(num_heads=1, key_dim=1)(query=input_layer, value=input_layer, key=input_layer)
flattened_output = Flatten()(attention_output)

dense1 = Dense(units=4128)(flattened_output)
dense1 = LeakyReLU()(dense1)

dense2 = Dense(units=2056)(dense1)
dense2 = LeakyReLU()(dense2)

dense3 = Dense(units=1028)(dense2)
dense3 = LeakyReLU()(dense3)

dense4 = Dense(units=516)(dense3)
dense4 = LeakyReLU()(dense4)

dense5 = Dense(units=256)(dense4)
dense5 = LeakyReLU()(dense5)

dense6 = Dense(units=128)(dense5)
dense6 = LeakyReLU()(dense6)

dense7 = Dense(units=34)(dense6)
dense7 = LeakyReLU()(dense7)
output = Dense(units=34, activation='softmax')(dense7)  # Softmax for multi-class classification

model = Model(inputs=input_layer, outputs=output)
model.compile(optimizer=SGD(learning_rate=0.001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Summary of the model
#model.summary()
#from data import X_train, y_train,X_validate, y_validate 



history = model.fit(dataset, epochs=2, batch_size=256, validation_data=(X_validate,y_validate))

#saved_model_path = 'D:\BOT TRAINING'
#tf.keras.models.save_model(model, saved_model_path)
#print(f"Saved model to {saved_model_path}")