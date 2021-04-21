import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.metrics import mean_squared_error

from keras import Sequential
from keras.layers import Dense

import board

# Board positions * count + starting pos + pieces exited + current_player
input_size = (40)*2+4+4+1

loaded_model = None
model_name = "None"

class Model:
    def __init__(self, model_name):
        if model_name == None:
            # Initialize neural network
            self.model = Sequential()
            self.model_name = "NewModel"

            # Add first hidden layer (and input layer)
            self.model.add(Dense(units=input_size, kernel_initializer='uniform', activation='relu', input_dim=input_size))

            # Add second hidden layer
            self.model.add(Dense(units=input_size, kernel_initializer='uniform', activation='relu'))

            # Add output layer
            self.model.add(Dense(units=1, kernel_initializer='uniform', activation='sigmoid'))

            self.model.compile(optimizer='adam', loss='mse')
        else:
            self.load_model(model_name)

    def load_model(self, filename):
        self.model = keras.models.load_model(f"models/{filename}_model")
        self.model_name = filename

    def train(self, data_filename):
        print("Starting Keras model training.")
        inputs = np.loadtxt(f"models/{data_filename}_inputs.txt", dtype=np.float32)
        outputs = np.loadtxt(f"models/{data_filename}_outputs.txt", dtype=np.float32)
        test_inputs = np.loadtxt(f"models/{data_filename}_test_inputs.txt", dtype=np.float32)
        test_outputs = np.loadtxt(f"models/{data_filename}_test_outputs.txt", dtype=np.float32)

        self.model.fit(
            inputs,
            outputs,
            batch_size=10,
            epochs=300,
            # We pass some validation for
            # monitoring validation loss and metrics
            # at the end of each epoch
            validation_data=(inputs, outputs))

        print("Training complete, testing...")

        pred_train = self.model.predict(inputs)
        print("Loss on train data: ", np.sqrt(mean_squared_error(outputs,pred_train)))

        pred = self.model.predict(test_inputs)
        print("Loss on test data: ", np.sqrt(mean_squared_error(test_outputs,pred))) 

        self.model.save(f"models/{data_filename}_model")
