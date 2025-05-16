#!/usr/bin/env python3
# train_vehicle_model.py

import os
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# load dataset
DATA_DIR   = "dataset/train"
IMG_SIZE   = (96, 96)
BATCH_SIZE = 32
VAL_SPLIT  = 0.20                                

datagen = ImageDataGenerator(
    rescale=1./255,
    horizontal_flip=True,
    rotation_range=10,
    zoom_range=0.10,
    width_shift_range=0.05,
    height_shift_range=0.05,
    validation_split=VAL_SPLIT,
)

train_gen = datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    subset="training",
)

val_gen = datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    subset="validation",
)

print("Class indices:", train_gen.class_indices)      # {'car':0, 'heavy':1}

# Model
base = tf.keras.applications.MobileNetV2(
    input_shape=(*IMG_SIZE, 3),
    alpha=0.35,                 # narrow band, low parameter
    include_top=False,
    weights="imagenet",
    pooling="avg",              # GlobalAveragePooling2D
)
base.trainable = False          # Stage 1 is only the upper layers

x = layers.Dense(64, activation="relu")(base.output)
out = layers.Dense(1, activation="sigmoid")(x)
model = models.Model(base.input, out)

# (car = 4×, heavy = 1×)
class_weight = {
    train_gen.class_indices["car"]:   4.0,
    train_gen.class_indices["heavy"]: 1.0,
}

# Compilation 
METRICS = [
    tf.keras.metrics.BinaryAccuracy(name="acc"),
    tf.keras.metrics.Precision(name="precision"),
    tf.keras.metrics.Recall(name="recall"),
]

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-3),
    loss="binary_crossentropy",
    metrics=METRICS,
)

# Feature extraction 
history = model.fit(
    train_gen,
    epochs=30,
    validation_data=val_gen,
    class_weight=class_weight,
)

base.trainable = True
for layer in base.layers[:-10]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-4),
    loss="binary_crossentropy",
    metrics=METRICS,
)

history_ft = model.fit(
    train_gen,
    epochs=10,
    validation_data=val_gen,
    class_weight=class_weight,
)

# INT8 quantization (TFLite-Micro) 
def rep_data():
    for _ in range(100):
        images, _ = next(train_gen)
        yield [images.astype("float32")]

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = rep_data
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type  = tf.uint8
converter.inference_output_type = tf.uint8
tflite_model = converter.convert()

with open("vehicle_classifier_int8.tflite", "wb") as f:
    f.write(tflite_model)

print("Done.")