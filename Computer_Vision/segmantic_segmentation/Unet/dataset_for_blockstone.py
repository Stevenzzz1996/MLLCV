# import glob
# import cv2
# import numpy as np
# x = glob.glob(r'C:/stone_segmataion/img/*.png')
# label = glob.glob(r'C:/stone_segmataion/label/*.png')
# print(x[0],label[0])


'''

make  datasets for stone segmantic segmentation by opencv and numpy when make samll dataset
train :3000
validation :600
test  : 339

'''
# labelsnp = []
# imgnp    = []
#
#
# for i in range(2720):
#     img      =cv2.imread(x[i])
#     labels   =cv2.imread(label[i],0)
#     print(" //" ,i ,'//')
#     img = [img]
#     labels = [labels]
# #     print(img.shape)
# #     img = np.expand_dims(img,axis=0)
# #     labels = np.expand_dims(labels,axis=0)
# #     print(img.shape)
# #     if i == 0:
# #         imgnp = img
# #         labelsnp = labels
# #     else:
# #         labelnp = np.concatenate((labels,labelsnp))
# #         imgnp    =   np.concatenate((img,imgnp))
# #         print(labelnp.shape)
# #
# # print(labelsnp.shape)
#     imgnp = img+imgnp
#     labelsnp = labels+labelsnp
# imgnp = np.asarray(imgnp)
# labelsnp = np.asarray(labelsnp)
# # print(imgnp.shape)
# np.save('img.npy',imgnp)
# np.save('label.npy',labelsnp)
#
# print('data is gone......')
#
# # x = np.load('img.npy')
# # print(x.shape)
from  collections import Counter
#
# x = np.load('img.npy')
# # print(x.shape)
# y =np.load('label.npy')
# print(np.max(y),np.min(y))
# print(Counter(y.flatten()))
# import matplotlib.pyplot as plt
#
# plt.imshow(y[1000])
# plt.show()
# for i in range(1000):
#     z = y[i]
#     print('show for iter',i,np.max(z),np.min(z))
# y[y>0]=1
# np.save('label.npy',y)
# print(Counter(y.flatten()))


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
'''
完成以下crop和resize
膨胀腐蚀开闭运算的代码

'''
x_all_all=np.load('img.npy')
y_all_all=np.load('label.npy')
# # x_train = x_all_all[0:2000]
# # y_train = y_all_all[0:2000]
# # x_val = x_all_all[2000:]
# # y_val = y_all_all[2000:]
# print(y_all_all.shape,x_all_all.shape)

x = x_all_all[0]
y = y_all_all[0]
# plt.imshow(x)
# plt.show()
# plt.imshow(y)
# plt.show()
# y = tf.expand_dims(y,axis = 2)
# x = tf.concat([x,y],axis = -1)
# print(x)
#
# x = tf.image.resize_with_crop_or_pad(x,int(np.random.rand()*960),int(1280*np.random.rand()))
# x = tf.image.resize(x,size = [960,1280])
# print(x)
# x = tf.cast(x,dtype = tf.int32)
# x_image = x[:,:,0:3]
# y = x[:,:,3]
# print(y)
# plt.imshow(x_image)
# plt.show()
# plt.imshow(y)
# plt.show()
# def da_crop_resize(x, y):
#     y = tf.expand_dims(y, axis=2)
#     image_all = tf.concat([x, y], axis=-1)
#     image_all = tf.image.resize_with_crop_or_pad(image_all, int(np.random.rand() * 960), int(1280 * np.random.rand()))
#     image_all = tf.image.resize(image_all, size=[960, 1280])
#     x = image_all[:, :, 0:3]
#     y = image_all[:, :, 3]
#     return  x,y
#
# # x,y = da_crop_resize(x,y)
# # x = tf.cast(x,dtype = tf.int32)
# # plt.imshow(x)
# # plt.show()
# # print(y)
# #缩放
def da_crop_padding(x,y):
    y = tf.expand_dims(y, axis=2)
    image_all = tf.concat([x, y], axis=-1)
    image_all = tf.image.resize_with_pad(image_all,int(np.random.rand() * 960), int(1280 * np.random.rand()))
    image_all = tf.image.resize(image_all, size=[960, 1280])
    x = image_all[:, :, 0:3]
    y = image_all[:, :, 3]
    return x, y

x,y = da_crop_padding(x,y)
x = tf.cast(x,dtype = tf.int32)
plt.imshow(x)
plt.show()
print(y)
y = tf.cast(y,dtype = tf.int32)
y = y*255
plt.imshow(y)
plt.show()


# def da_crop_padding(x,y):
#     y = tf.expand_dims(y, axis=2)
#     image_all = tf.concat([x, y], axis=-1)
#     image_all = tf.image.resize_with_pad(image_all,int(np.random.rand() * 960), int(1280 * np.random.rand()))
#     image_all = tf.image.resize(image_all, size=[960, 1280])
#     x = image_all[:, :, 0:3]
#     y = image_all[:, :, 3]
#
#     return x, y
# #裁剪
def da_crop_resize(x, y):
    y = tf.expand_dims(y, axis=2)
    image_all = tf.concat([x, y], axis=-1)
    image_all = tf.image.resize_with_crop_or_pad(image_all, int(np.random.rand() * 960), int(1280 * np.random.rand()))
    image_all = tf.image.resize(image_all, size=[960, 1280])
    x = image_all[:, :, 0:3]
    y = image_all[:, :, 3]

    return  x,y
for i  in range (4):
    if np.random.rand()>0.5:
            x,y = da_crop_padding(x,y)
    else:
            x,y = da_crop_resize(x, y)


    x = tf.cast(x,dtype = tf.int32)
    plt.imshow(x)
    plt.show()
    print(y)
    y = tf.cast(y,dtype = tf.int32)
    y = y*255
    plt.imshow(y)
    plt.show()
# z = y
# z = tf.cast(z,dtype = tf.int64)
#
# acc = tf.reduce_sum(tf.cast(tf.equal(y, y), dtype=tf.int32))/(1280*960)
# print(acc)
for i in range(300):
    print(np.random.rand())