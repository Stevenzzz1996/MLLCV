import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sklearn
import pandas as pd
import os
import sys
import time
import tensorflow as tf
from  tensorflow.keras import layers, optimizers, datasets, Sequential,losses,metrics
# from sunet import Unet
from model import Unet
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import math
print(tf.__version__) #打印一下版本的问题
print(sys.version_info)
for module in mpl,np,pd,sklearn:
    print(module.__name__,module.__version__)
import cv2
import tqdm
import csv
#缩放
def da_crop_padding(x,y):
    y = tf.expand_dims(y, axis=2)
    image_all = tf.concat([x, y], axis=-1)
    image_all = tf.image.resize_with_pad(image_all,int(np.random.rand() * 960), int(1280 * np.random.rand()))
    image_all = tf.image.resize(image_all, size=[960, 1280])
    x = image_all[:, :, 0:3]
    y = image_all[:, :, 3]

    return x, y
#裁剪
def da_crop_resize(x, y):
    y = tf.expand_dims(y, axis=2)
    image_all = tf.concat([x, y], axis=-1)
    image_all = tf.image.resize_with_crop_or_pad(image_all, int(np.random.rand() * 960), int(1280 * np.random.rand()))
    image_all = tf.image.resize(image_all, size=[960, 1280])
    x = image_all[:, :, 0:3]
    y = image_all[:, :, 3]

    return  x,y

def preprocess(x, y):
    '''   data  arument for segmentation '''
    # if np.random.rand()>0.5:
    #     x = x[0]
    #     x = tf.image.flip_left_right(x)
    #     x =tf.expand_dims(x,axis = 0)
    #
    #     y = y[0]
    #     y = tf.image.flip_left_right(y)
    #     y = tf.expand_dims(y, axis=0)
    '''base on trian'''
    print(np.random.rand(),x.shape,y.shape)
    if np.random.rand()>0.5:
        x,y = da_crop_padding(x,y)
    else:
        x,y = da_crop_resize(x, y)

    print('1')

    x = tf.cast(x, dtype=tf.float32)
    y = tf.cast(y, dtype=tf.int32)
    y = tf.one_hot(y,depth = 2)
    return x,y
x_all_all=np.load('img.npy')
y_all_all=np.load('label.npy')
# x_train = x_all_all[0:2000]
# y_train = y_all_all[0:2000]
# x_val = x_all_all[2000:]
# y_val = y_all_all[2000:]
print(y_all_all.shape,x_all_all.shape)
train_db = tf.data.Dataset.from_tensor_slices((x_all_all[50:],y_all_all[50:]))
train_db = train_db.shuffle(200).map(preprocess).batch(1)
test_db = tf.data.Dataset.from_tensor_slices((x_all_all[0:50],y_all_all[0:50]))
test_db = test_db.map(preprocess).batch(1)
next(iter(train_db))
next(iter(test_db))
print(y_all_all.shape,x_all_all.shape)
model =Unet(num_class=2)

#model.load_weights('C:/stone_segmataion/callbacks/slate_models.h5')
logdir = '.\callbacks'
if not os.path.exists(logdir):
    os.mkdir(logdir)
output_model_file = os.path.join(logdir,'slate_models2.h5')

callbacks = [
    tf.keras.callbacks.TensorBoard(logdir),
    tf.keras.callbacks.ModelCheckpoint(output_model_file,monitor='val_acc', save_best_only=True),
    # tf.keras.callbacks.EarlyStopping(monitor='val_accuracy',patience =10,min_delta = 0.1)
]

def focal(y_ture,y_pre):
    loss = -tf.reduce_mean( y_ture*tf.multiply(1-y_pre,1-y_pre)*tf.math.log(tf.clip_by_value(y_pre,1e-10,1.0)))*0.25
    return loss
# def meanIOU(y_ture,y_pre):
#
#
#
# #'categorical_crossentropy'
model.compile(loss =focal,
              optimizer=optimizers.Adam(lr=1e-4),
              metrics = ['acc'])
model.fit(train_db,epochs =100,validation_data =test_db,callbacks=callbacks,steps_per_epoch=3)



