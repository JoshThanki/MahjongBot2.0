from imports import *

#optional (gpu settings)
gpus = tf.config.list_physical_devices('GPU')
if gpus: 
    tf.config.set_logical_device_configuration(
        gpus[0],
        [tf.config.LogicalDeviceConfiguration(memory_limit=6000)]
    )
logical_gpus = tf.config.list_logical_devices('GPU')
print(len(gpus), "Physical GPU,", len(logical_gpus), "Logical GPUs")

#DEFINING MODEL
input_layer = Input(shape=(510, 1))

#Multihead Attention Layer at the start (number of heads is 1 as in the paper). Can try more heads.
attention_output = MultiHeadAttention(num_heads=1, key_dim=1)(query=input_layer, value=input_layer, key=input_layer)
flattened_output = Flatten()(attention_output)

# Dense layers with leakyReLU inbetween
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

#defining and compiling model
model = Model(inputs=input_layer, outputs=output)
model.compile(optimizer=SGD(learning_rate=0.001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

#model.summary()


from data import X_train, y_train,X_validate, y_validate 

#training model
history = model.fit(X_train, y_train, epochs=1, batch_size=256, validation_data=(X_validate, y_validate ))

# saving model
saved_model_path = 'D:\BOT TRAINING'
tf.keras.models.save_model(model, saved_model_path)
print(f"Saved model to {saved_model_path}")