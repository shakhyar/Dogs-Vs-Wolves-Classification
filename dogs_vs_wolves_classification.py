# -*- coding: utf-8 -*-
"""dogs_vs_wolves_classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12Tm2M_-Dd56YA66ijmcHjdB1i2JZKE-F
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import PIL
import tensorflow as tf

from tensorflow import keras
from keras.optimizers import SGD

from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

from google.colab import drive
drive.mount('/content/drive')

os.environ['KAGGLE_CONFIG_DIR'] = "/content/drive/MyDrive/Kaggle"
# /content/drive/My Drive/Kaggle is the path where kaggle.json is present in the Google Drive

# Commented out IPython magic to ensure Python compatibility.
#changing the working directory
# %cd /content/drive/MyDrive/Kaggle
#Check the present working directory using pwd command

"""**Download the dataset**"""

# !kaggle datasets download -d harishvutukuri/dogs-vs-wolves --force

#unzipping the zip files and deleting the zip files
# !unzip \*.zip  && rm *.zip

import pathlib
# add your dataset destination below
data_dir = tf.keras.utils.get_file('/content/drive/MyDrive/Kaggle/data', origin="/content/drive/MyDrive/Kaggle/data")
data_dir = pathlib.Path(data_dir)

dogs = list(data_dir.glob('dogs/*'))
PIL.Image.open(str(dogs[10]))

batch_size = 64
img_height = 300
img_width = 300
epochs = 40
num_classes = 2

train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="training",
    seed=128,
    image_size=(img_height, img_width)
)
val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="validation",
    seed=128,
    image_size=(img_height,img_width)
)
class_names = train_ds.class_names
print(class_names)

AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.cache().shuffle(100).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

augmentation_layer = keras.Sequential(
    [
     layers.experimental.preprocessing.RandomFlip("horizontal",
                                    input_shape=(img_height, img_width, 3)),
     layers.experimental.preprocessing.RandomRotation(0.1),
     layers.experimental.preprocessing.RandomRotation(0.2),
     layers.experimental.preprocessing.RandomZoom(0.2)
    ]
)

normalization_layer = layers.experimental.preprocessing.Rescaling(1./255)

opt = SGD(learning_rate=0.001)


model = keras.Sequential(
    [
     augmentation_layer,
     normalization_layer,
     layers.Conv2D(64, 3, padding='same', activation='elu'),
     layers.MaxPooling2D(),
     
     layers.Conv2D(32, 3, padding='same', activation='elu'),
     layers.MaxPooling2D(),
     
     layers.Conv2D(16, 3, padding='same', activation='elu'),
     layers.MaxPooling2D(),

     layers.Conv2D(16, 3, padding='same', activation='elu'),
     layers.MaxPooling2D(),
     
     layers.Dense(128, activation='relu'),

     layers.Conv2D(16, 3, padding='same', activation='elu'),
     layers.MaxPooling2D(),

     layers.Dropout(0.1),
     layers.BatchNormalization(),
     layers.Flatten(),

     layers.Dense(128, activation='relu'),
     layers.Dense(num_classes, activation='sigmoid')
    ]
)

model.compile(optimizer=opt, loss=tf.keras.losses.SparseCategoricalCrossentropy(),
              metrics=['accuracy'])
model.summary()

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=epochs, 
    batch_size=batch_size
)

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(epochs)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

"""**Inference**"""

x = True
print("type 'exit' to quit")
while x:
    test_url = input("\nenter the url for your image\n>>> ")
    if test_url == "exit":
        x = False
    else:
        l = test_url.split('/')
        filename = l[-1]
        test_path = tf.keras.utils.get_file(filename, origin=test_url)
        img = keras.preprocessing.image.load_img(
        test_path, target_size=(img_height, img_width)
        )
        img_array = keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0) # Create a batch

        predictions = model.predict(img_array)
        score = tf.nn.softmax(predictions[0])
        print(
        "Predicted: {} ... Accuracy: {:.2f}% ..."
        .format(class_names[np.argmax(score)], 100 * np.max(score))
        )
