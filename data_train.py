import os
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import argparse

from scipy import interpolate
from itertools import cycle
from sklearn import svm, datasets
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize
from tensorflow.keras.preprocessing import image
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import telebot
from telebot import types
from keras.models import load_model
from keras.preprocessing import image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
def load_image(img_path):
    img = image.load_img(img_path, target_size=(200, 200))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_image(model, image_path):
    img = load_image(image_path)
    classes = model.predict(img)
    if classes[0] < 0.5:
        print(image_path + " is a people")
    else:
        print(image_path + " is a bears")

def main(train_dir, valid_dir, test_files_path):
    print('Train directory:', train_dir)
    print('Validation directory:', valid_dir)
    print('Test files directory:', test_files_path)

    train_datagen = ImageDataGenerator(rescale=1/255)
    validation_datagen = ImageDataGenerator(rescale=1/255)

    train_generator = train_datagen.flow_from_directory(
        train_dir, 
        classes=['people', 'bears'],
        target_size=(200, 200),
        batch_size=110,
        class_mode='binary')

    validation_generator = validation_datagen.flow_from_directory(
        valid_dir, 
        classes=['people', 'bears'],
        target_size=(200, 200),
        batch_size=100,
        class_mode='binary',
        shuffle=False)

    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(200, 200, 3)),
        tf.keras.layers.Dense(128, activation=tf.nn.relu),
        tf.keras.layers.Dense(1, activation=tf.nn.sigmoid)
    ])

    model.summary()

    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    history = model.fit(
        train_generator,
        steps_per_epoch=16,
        epochs=18,
        verbose=1,
        validation_data=validation_generator,
        validation_steps=8
    )

    while True:
        test_file_name = input("Enter the name of the test file or 'q' to quit: ")
        if test_file_name.lower() == 'q':
            break
        test_file_path = os.path.join(test_files_path, test_file_name)
        if not os.path.exists(test_file_path):
            print("File not found.")
            continue
        predict_image(model, test_file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Path arguments for train, validation, and test files directories.')
    parser.add_argument('train_dir', type=str, help='Path to the training directory')
    parser.add_argument('valid_dir', type=str, help='Path to the validation directory')
    parser.add_argument('test_files_path', type=str, help='Path to the test files directory')
    args = parser.parse_args()

    main(args.train_dir, args.valid_dir, args.test_files_path)