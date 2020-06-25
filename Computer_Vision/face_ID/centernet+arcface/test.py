import pymysql
import ffmpeg
import cv2
from centerface import CenterFace
from api import detect,align
from emotion_net import LABELS,mini_XCEPTION
import numpy as np
import tensorflow as tf
'''
人脸检测
人脸识别
人脸对齐
连接ffmpeg
连接mysql
'''

#情绪识别网络结构定义
emotion_model = mini_XCEPTION(input_shape=(64,64,1),num_classes=7)
emotion_model.summary()
emotion_model.load_weights('C:/Users/24991/Desktop/emotion/emotion/emotion/emotion.hdf5')


def puttext(src,res): #res[第几个人][人脸数据][xmin,ymin,xmax,ymax,classfication]
    nums = len(res)

    for i in range(nums):
        print(res[0][0])

        # emotion_situation = emotion_test(src,int(res[i][0][0]),int(res[i][0][1]),int(res[i][0][2]),int(res[i][0][3]))
        # print(tf.argmax(emotion_situation))
        #写入关键信息
        src = cv2.rectangle(src,(int(res[i][0][0]),int(res[i][0][1])),(int(res[i][0][2]),int(res[i][0][3])),(i*10,i*20,i*15),thickness=1)
        src = cv2.putText(src,'person: '+str(res[i][0][4]),(int(res[i][0][0]),int(res[i][0][1])),cv2.FONT_HERSHEY_SIMPLEX,1.2,(i*10,i*20,i*15),2)
        #person-> arcface
        # classfication
    return src
def emotion_test(src,xmin,ymin,xmax,ymax):
    #crop face image
    src_gary = cv2.cvtColor(src,cv2.COLOR_BGR2GRAY)
    src_gary = src_gary/255. -0.5
    crop_face = src_gary[ymin:ymax,xmin:xmax]
    crop_face = cv2.resize(crop_face,(64,64))
    data_model_size = crop_face[np.newaxis,:,:,np.newaxis]
    print(data_model_size.shape)
    data_model_size = tf.cast(data_model_size,dtype=tf.float32)
    emotion_situation = emotion_model(data_model_size)
    return emotion_situation

def face_align(im,res,tsize=128, desiredLeftEye=0.35):
    crop = []
    for (det, lm) in res:
        left_eye = lm[2:4]
        right_eye = lm[0:2]
        # compute the angle between the eye centroids
        dY = right_eye[1] - left_eye[1]
        dX = right_eye[0] - left_eye[0]
        angle = np.degrees(np.arctan2(dY, dX)) - 180

        # compute X distance, because we want to align the face
        # make it Y1 = Y2
        desiredRightEye = 1.0 - desiredLeftEye
        dist = np.sqrt((dX ** 2) + (dY ** 2))
        desiredDist = desiredRightEye - desiredLeftEye
        desiredDist *= tsize
        scale = desiredDist / dist

        eyesCenter = (left_eye[0] + right_eye[0]) // 2, (left_eye[1] + right_eye[1]) // 2
        M = cv2.getRotationMatrix2D(eyesCenter, angle, scale)
        tX = tsize * 0.5
        tY = tsize * desiredLeftEye
        M[0, 2] += (tX - eyesCenter[0])
        M[1, 2] += (tY - eyesCenter[1])

        (w, h) = (tsize, tsize)
        output = cv2.warpAffine(im, M, (w, h), flags=cv2.INTER_CUBIC)
        crop.append(output)
    return crop
#  def_face_regonition()
#开启摄像头人脸检测
cap = cv2.VideoCapture(0)
while 1:
    ret,frame = cap.read() #读取视频
    frame = cv2.flip(frame,1)
    res = detect(frame)
    print('res',res,len(res))
    if len(res)>0:

        frame = puttext(frame,res)

    else:
        frame = frame
    cv2.imshow('video',frame)
    if cv2.waitKey(100) & 0xff == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
