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
def puttext(src,res): #res[第几个人][人脸数据][xmin,ymin,xmax,ymax,classfication]
    nums = len(res)

    for i in range(nums):
        print(res[0][0],res[0][1])

        # emotion_situation = emotion_test(src,int(res[i][0][0]),int(res[i][0][1]),int(res[i][0][2]),int(res[i][0][3]))
        # print(tf.argmax(emotion_situation))
        #写入关键信息
        src = cv2.rectangle(src,(int(res[i][0][0]),int(res[i][0][1])),(int(res[i][0][2]),int(res[i][0][3])),((i+3)*10,(i+3)*20,(i+3)*15),thickness=2)
        src = cv2.putText(src,'face: '+str(res[i][0][4]),(int(res[i][0][0]),int(res[i][0][1])),cv2.FONT_HERSHEY_SIMPLEX,1,((i+5)*10,(i+5)*20,(i+5)*15),2)
        for t in range(1,10,2):
            src = cv2.circle(src,(int(res[i][1][t-1]),int(res[i][1][t])),2,(100,200,22),2)
        #person-> arcface
        # classfication
    return src

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

#开启摄像头人脸检测
cap = cv2.VideoCapture(0)
while 1:
    ret,frame = cap.read() #读取视频
    frame = cv2.flip(frame,1)
    res = detect(frame)
    # print('res',res,len(res))
    if len(res)>0:

        frame = puttext(frame,res)
        # crop_image = face_align(frame,res)
        # crop_image = np.array(crop_image)
        #print(crop_image.shape)
        #cv2.imshow('face',crop_image[0])
        # cv2.imshow('face:',frame)


    else:
        frame = frame
    cv2.imshow('video',frame)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()