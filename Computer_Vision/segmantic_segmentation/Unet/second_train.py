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
def da_crop_padding(x,y,t):
    y = tf.expand_dims(y, axis=2)
    image_all = tf.concat([x, y], axis=-1)
    s = np.random.rand()
    image_all = tf.image.resize_with_pad(image_all,int((s+0.05) * 960), int(1280 * (t+0.05)))
    image_all = tf.image.resize(image_all, size=[960, 1280])
    x = image_all[:, :, 0:3]
    y = image_all[:, :, 3]

    return x, y
#裁剪
def da_crop_resize(x, y,t):
    y = tf.expand_dims(y, axis=2)
    image_all = tf.concat([x, y], axis=-1)
    s =np.random.rand()
    image_all = tf.image.resize_with_crop_or_pad(image_all, int((s+0.05) * 960), int(1280 * (t+0.05)))
    image_all = tf.image.resize(image_all, size=[960, 1280])
    x = image_all[:, :, 0:3]
    y = image_all[:, :, 3]

    return  x,y
x_all_all=np.load('img.npy')
y_all_all=np.load('label.npy')
print(y_all_all.shape,x_all_all.shape)
train_db = tf.data.Dataset.from_tensor_slices((x_all_all,y_all_all))
train_db = train_db.shuffle(200).batch(1)
test_db = tf.data.Dataset.from_tensor_slices((x_all_all[0:50],y_all_all[0:50]))
test_db = test_db.batch(1)
next(iter(train_db))
next(iter(test_db))
print(y_all_all.shape,x_all_all.shape)
model = Unet(num_class=2)
model.load_weights('C:/stone_segmataion/callbacks/slate_models.h5')

def focal(y_ture,y_pre):
    loss = -tf.reduce_mean( y_ture*tf.multiply(1-y_pre,1-y_pre)*tf.math.log(tf.clip_by_value(y_pre,1e-10,1.0)))*0.25
    return loss
def meanIOU(y_ture,y_pre):

    y_pre = y_pre[0]
    y_ture = y_ture[0]
    y_ture = tf.argmax(y_ture,axis = 2)
    y_pre = tf.argmax(y_pre,axis = 2)
    y_positive = tf.reduce_sum(tf.cast(tf.equal(y_pre, y_ture), dtype=tf.int32))
    y_pre_sum = tf.reduce_sum(y_pre)
    y_pre_sum =tf.cast(y_pre_sum,dtype = tf.int32)
    y_ture_sum = tf.reduce_sum(y_ture)
    y_ture_sum =tf.cast(y_ture_sum,dtype = tf.int32)
    acc = y_positive/(y_pre_sum+y_ture_sum-y_positive)
    return acc

def pixelacc(y_ture,y_pre):
    y_pre = y_pre[0]
    y_ture = y_ture[0]
    y_ture = tf.argmax(y_ture, axis=2)
    y_pre = tf.argmax(y_pre, axis=2)
    acc = tf.reduce_sum(tf.cast(tf.equal(y_pre, y_ture), dtype=tf.int32))/1228800
    return acc

# #'categorical_crossentropy'
def main():

    # [b, 32, 32, 3] => [b, 1, 1, 512]

    optimizer = optimizers.Adam(lr=1e-4)

    for epoch in range(500):

        for step, (x,y) in enumerate(train_db):

            with tf.GradientTape() as tape:
                t = np.random.rand()
                z = np.random.rand()
                if t > 0.5:
                    x, y = da_crop_padding(x[0], y[0],t)
                elif 0.5>t>0.2:
                    x, y = da_crop_resize(x[0], y[0],z)
                else:
                    x,y = x[0],y[0]

                x = tf.cast(x,dtype = tf.float32)
                y = tf.cast(y, dtype=tf.int32)
                y = tf.one_hot(y,depth = 2)
                x = tf.expand_dims(x,axis = 0)
                y = tf.expand_dims(y,axis = 0)
                logits = model(x)
                loss = focal(y_ture = y,y_pre=logits)

            grads = tape.gradient(loss, model.trainable_variables)
            optimizer.apply_gradients(zip(grads, model.trainable_variables))
            if step %50 == 0:
                pixacc = pixelacc(y_pre=logits,y_ture=y)

                print('GDUT Computer Vision research computing for slate segmentation  周期：',
                      epoch, '~~~~~~~~~~~~~~~~~~   步长：',step, '*************   loss:', float(loss),
                      '&&&&&&&&&&&&&   pixel_acc:',round(float(pixacc),3),'meanIOU:继续得写写.....')
            if step % 500 == 0:
                show = tf.cast(tf.argmax(logits[0], axis=2), dtype=tf.int32)
                source = tf.cast(tf.argmax(y[0], axis=2), dtype=tf.int32)
                plt.figure(figsize=(24, 8))
                plt.subplot(1, 2, 1)
                plt.imshow(show)
                plt.title('slate source image' + str(step), fontsize=20)
                plt.subplot(1, 2, 2)
                plt.imshow(source)
                plt.savefig('C:/stone_segmataion/train_output_flow/'+str(epoch)+str(step/500)+'.png')
        if epoch % 2 == 0:
            tf.saved_model.save(model, 'model')

        # '''test and save model for segmatation'''
        # total_num = 0
        # total_correct = 0
        # for x,y in test_db:
        #     print("the model test is computing...........")
        #     logits = model(x)
        #     pred = tf.argmax(logits, axis=2)
        #     pred = tf.cast(pred, dtype=tf.int32)
        #
        #     correct = tf.cast(tf.equal(pred, y), dtype=tf.int32)
        #     correct = tf.reduce_sum(correct)
        #
        #     total_num += x.shape[0]
        #     total_correct += int(correct)
        #
        # acc = total_correct / total_num
if __name__ == '__main__':
    main()
