"""
Author: Alex Hamilton - https://github.com/alexhamiltonRN
Created: 2018-11-18
Description: CNN training using t2 images from ProstateX challenge. 
"""

import keras
from keras import layers
from keras import models
from keras import regularizers
from keras.utils import plot_model

import training_plots

import numpy as np
from pathlib import Path

# LOADING THE DATA
t2_samples = np.load('/home/alexander/Documents/DataProjects/Data/MBI/ProstateX/generated/train/numpy/t2/X_train.npy')
t2_labels = np.load('/home/alexander/Documents/DataProjects/Data/MBI/ProstateX/generated/train/numpy/t2/Y_train.npy')

# CONVERT IMAGE SAMPLES TO FLOAT32 (REDUCE PRECISION FROM FLOAT64)
t2_samples_flt32 = np.array(t2_samples, dtype=np.float32, copy = True)

# RESHAPE IMAGE SAMPLES TO INCLUDE A SINGLE CHANNEL
x_train = t2_samples_flt32.reshape((620,32,32,1))
y_train = t2_labels

# MODEL SPECIFICATION
model = models.Sequential()

model.add(layers.Conv2D(32, kernel_size=(3,3), padding = 'same', activation='relu', input_shape=(32,32,1))) 
model.add(layers.Conv2D(32, (3,3), activation='relu'))
model.add(layers.Dropout(0.5))
model.add(layers.MaxPooling2D((2,2)))
model.add(layers.Dropout(0.5))

model.add(layers.Conv2D(64, (3,3), padding = 'same', activation='relu'))
model.add(layers.Conv2D(64, (3,3), activation='relu'))
model.add(layers.Dropout(0.5))
model.add(layers.MaxPooling2D((2,2)))
model.add(layers.Dropout(0.5))

model.add(layers.Flatten())
model.add(layers.Dropout(0.5))

model.add(layers.Dense(512,activation='relu'))
model.add(layers.Dropout(0.5))

model.add(layers.Dense(256, activation='relu'))
model.add(layers.Dropout(0.5))

model.add(layers.Dense(128, kernel_regularizer = regularizers.l1_l2(l1=0.0001, l2=0.0001), activation='relu'))
model.add(layers.Dropout(0.5))

model.add(layers.Dense(1, activation='sigmoid'))
model.summary()

# COMPILATION
opt = keras.optimizers.Adadelta()
model.compile(optimizer=opt, loss='binary_crossentropy', metrics=['accuracy'])

# FIT
history = model.fit(x_train, y_train, epochs=100, validation_split=0.25, class_weight={0:1,1:2}, batch_size=80, shuffle=True)

# PLOT ACCURACY/VALIDATION CURVES
plot_model(model, to_file='t2_model.png', show_shapes = True)
training_plots.plot_metrics(history, 'T2')