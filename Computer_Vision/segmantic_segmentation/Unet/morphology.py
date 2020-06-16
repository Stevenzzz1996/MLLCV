import cv2
import matplotlib.pyplot as plt
import  tensorflow as tf
import numpy as np
import glob
import os
# c = cv2.imread('C:/stone_segmataion/train_output_flow/362.0.png')
# kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))#定义一个结构元素
# c = cv2.morphologyEx(c,cv2.MORPH_OPEN,kernel)#进行相关操作
# print(c.shape)
#
#
# t = cv2.imread('C:/stone_segmataion/img.png')
# print(t.shape)
# t = tf.cast(t,dtype = tf.float32)
# t = tf.expand_dims(t,axis = 0)
# t1 = tf.image.resize(t,size = [960,1280])
# print(t1.shape)
# model = tf.saved_model.load('C:/stone_segmataion/model')
# t = model(t1)
# t = tf.argmax(t[0],axis = 2)
# plt.figure(figsize=(24, 8))
# plt.subplot(1,2,1)
# plt.imshow(t)
# plt.subplot(1,2,2)
# img = tf.cast(t1[0],dtype = tf.int32)
# plt.imshow(img)
# plt.show()
# model = tf.saved_model.load('C:/stone_segmataion/model')
#
#
#
# path_list = glob.glob(r'C:/stonedatase/json_1/1_json/*.png')
# # path_list2 = os.listdir('C:/stonedatase/')
# print(path_list[0])
# # print(path_list2)
# img_data = []
# img_ones  = tf.ones(shape=(960,1280))
# for i in range(46):
#     z = str(i+1)
#     path_list = glob.glob(r'C:/stonedatase/json_1/'+z+'_json/*.png')
#     img = cv2.imread(path_list[0])
#     img = tf.cast(img,dtype = tf.float32)
#     img = tf.expand_dims(img,axis = 0)
#     img = tf.image.resize(img,size = [960,1280])
#     img = model(img)
#     t = tf.argmax(img[0],axis = 2)
#     t  =tf.cast(t,dtype =tf.float32)
#     img_ones = tf.concat([img_ones,t],axis = 0)
#
#     print(i)
#
#
# img_ones = tf.cast(img_ones,dtype = tf.int32)
# print(img_ones.shape)
# img_ones = np.asarray(img_ones)
# img_ones = img_ones*255
#
# cv2.imwrite('C:/stone_segmataion/test.png',img_ones)
'''
model pruning 



'''
import tensorflow_model_optimization as tfmot
import tensorflow as tf
import numpy as np
x_all_all=np.load('img.npy')
y_all_all=np.load('label.npy')
# x_train = x_all_all[0:2000]
# y_train = y_all_all[0:2000]
# x_val = x_all_all[2000:]
# y_val = y_all_all[2000:]
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
    x = tf.cast(x, dtype=tf.float32)
    y = tf.cast(y, dtype=tf.int32)
    y = tf.one_hot(y,depth = 2)
    return x,y
print(y_all_all.shape,x_all_all.shape)
train_db = tf.data.Dataset.from_tensor_slices((x_all_all[50:],y_all_all[50:]))
train_db = train_db.shuffle(200).map(preprocess).batch(1)
test_db = tf.data.Dataset.from_tensor_slices((x_all_all[0:50],y_all_all[0:50]))
test_db = test_db.map(preprocess).batch(1)
next(iter(train_db))
next(iter(test_db))
print(y_all_all.shape,x_all_all.shape)
model = tf.keras.models.load_model('C:\model')
pruning_schedule = tfmot.sparsity.keras.PolynomialDecay(
 initial_sparsity=0.0, final_sparsity=0.5,
 begin_step=2000, end_step=4000)
model_for_pruning = tfmot.sparsity.keras.prune_low_magnitude(model,
    pruning_schedule=pruning_schedule)
model_for_pruning.compile(
    loss=tf.keras.losses.categorical_crossentropy,
    optimizer='adam',
    metrics=['accuracy'])
model_for_pruning.summary()



