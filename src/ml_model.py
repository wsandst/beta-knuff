import numpy as np
import tensorflow as tf
from tensorflow import keras

from keras import Sequential
from keras.layers import Dense

import board

# Board positions * count + starting pos + pieces exited + current_player
input_size = (40)*2+4+4+1

class Model:
    def __init__(self):
        # Initialize neural network
        self.nnet = Sequential()

        # Add first hidden layer (and input layer)
        self.nnet.add(Dense(units=input_size, kernel_initializer='uniform', activation='relu', input_dim=input_size))

        # Add second hidden layer
        self.nnet.add(Dense(units=24, kernel_initializer='uniform', activation='relu'))

        # Add output layer
        self.nnet.add(Dense(units=1, kernel_initializer='uniform', activation='sigmoid'))

        self.nnet.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])