import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sklearn
import pandas as pd
import os
import sys
import time
import tensorflow as tf
from  sklearn.preprocessing import StandardScaler
from  tensorflow.keras import layers, optimizers, datasets, Sequential,losses,metrics
# from sunet import Unet
from model import Unet
from sklearn.decomposition import PCA
# os.environ["CUDA_VISIBLE_DEVICES"] = "3"
import math
print(tf.__version__) #打印一下版本的问题
print(sys.version_info)
for module in mpl,np,pd,sklearn:
    print(module.__name__,module.__version__)
import glob
import cv2
from collections import Counter
import csv
from PIL import Image

#------------------------------------------------------------------------------------
'''
数据集制作

'''
'''time = 0
imagedata =[]
WSI_MASK_PATH = 'C:/Users/Administrator/Downloads/test_dataset (1)'#存放图片的文件夹路径
paths = glob.glob(os.path.join(WSI_MASK_PATH, '*.jpg'))
print(paths)
for path in paths:
    img= cv2.imread(path)
    #print(img)
    image = [img]
    print(img.shape)
    imagedata += image
    time += 1
    if time % 10 == 0:
        print('导入数据集中', time, '/20000')
x_train_all = np.asarray(imagedata)
np.save('xtest.npy',x_train_all)'''


def preprocess(x):
    # [-1~1]
    x = tf.cast(x, dtype=tf.float32)
    return x
x_all_all=np.load('img.npy',allow_pickle = True)
print(x_all_all.shape,x_all_all.dtype)
print(x_all_all.shape)
model = Unet(num_class=2)
model.load_weights('C:/stone_segmataion/callbacks/slate_models.h5')
writefile = './test.txt'
file_to_write = open(writefile, 'w')
for i in range(50):
    x = x_all_all[i:i+1]
    x =tf.cast(x,dtype=tf.float32)
    y = model(x)
    print(y.shape)
    y = np.asarray(y)
    y = tf.argmax(y[0],axis=2)
    print(y.shape)
    y = y*255
    plt.figure(figsize=(24, 8))
    plt.subplot(1, 2, 1)
    plt.imshow(x_all_all[i])
    plt.title('slate source image' + str(i), fontsize=20)
    plt.subplot(1, 2, 2)
    plt.imshow(y)
    plt.colorbar()
    plt.title('slate segmentation image'+str( i), fontsize=20)
    path = 'C:/stone_segmataion/seg1/'+str(i)+'.png'
    plt.savefig(path)
#     # y[y==25] =0
#     # print(y.dtype)
#     # num = 7000+i
#     # strnum = str(num)
#     # c = 'C:/stone_segmataion/seg1/'
#     # strnum = '00'+str(num)
#     # path = c+strnum+'.png'
#     # cv2.imwrite(path,y)
#     #
#     # # 原图
#     # d = 'C:/stone_segmataion/seg/'
#     # path = d + strnum + '.png'
#     # cv2.imwrite(path, x_all_all[i])
#
#     #
#     # print(i)
#
#     # y = Counter(y.flatten())
#     # # print(y)
#     # y = str(y)
#     # y = y[9:-2]
#     # print(y)
#     # y = y.replace(':',',')
#     # num = 7000+i
#     # strnum = str(num)
#     # c = '00'+strnum+'.jpg,'+ '1,'+y
#     # print(c)
#     # file_to_write.write(c)
#     # file_to_write.write('\n')
#
# # x_all_all=np.load('img.npy',allow_pickle = True)
# # y = np.load('label.npy')
#
# # x = tf.image.flip_left_right(x_all_all[0])
# # print(x)
# # plt.imshow(x)
# # plt.show()
# # plt.imshow(x_all_all[0])
# # plt.show()
#
# # x = tf.expand_dims(x_all_all[0],axis = 0)
# # print(x.shape)
# print(np.random.rand())
#
# # x = tf.image.crop_and_resize()
# # plt.show()
# # y = tf.image.flip_left_right(y[0])
# x_all_all=np.load('label.npy',allow_pickle = True)
# print(x_all_all.shape)


































