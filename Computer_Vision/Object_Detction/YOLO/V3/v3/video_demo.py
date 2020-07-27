import cv2
import time
import numpy as np
import core.utils as utils
import tensorflow as tf
from core.yolov3 import YOLOv3, decode

from core.LLmodel import LLYOLO
from core.yolo_model import YOLO

'''
调用h5文件
'''
# model = YOLO()
# model.build(input_shape=(None,416,416,3))
# model.load_weights('C:/Users/24991/Desktop/YOLOV3/small_yolo.h5')
# model.summary()

'''
调用pb文件
'''
model = tf.keras.models.load_model('small_yolo')
vid = cv2.VideoCapture(1) #外接摄像头为1，内置为0
# vid.open(1)
input_size = 416
while True:
    return_value, frame = vid.read()
    if return_value:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame,1)
    else:
        raise ValueError("No image!")
    frame_size = frame.shape[:2]
    image_data = utils.image_preporcess(np.copy(frame), [input_size, input_size])
    image_data = image_data[np.newaxis, ...].astype(np.float32)
    #print(image_data.shape)
    prev_time = time.time()
    feature_maps = model(image_data,training = None)
    curr_time = time.time()
    exec_time = curr_time - prev_time
    # print(exec_time)

    bbox_tensors = []
    for i in range(1,6,2):
        bbox_tensor =feature_maps[i]
        #print(i)
        bbox_tensors.append(bbox_tensor)
    pred_bbox = bbox_tensors
    pred_bbox = [tf.reshape(x, (-1, tf.shape(x)[-1])) for x in pred_bbox]
    #print('data:',np.max(pred_bbox[0][:,5:6]))
    pred_bbox = tf.concat(pred_bbox, axis=0)
    #print(pred_bbox.shape)
    bboxes = utils.postprocess_boxes(pred_bbox, frame_size, input_size, 0.7)
    print(bboxes.shape)
    bboxes = utils.nms(bboxes, 0.45, method='nms')
    print(bboxes)
    image = utils.draw_bbox(frame, bboxes)

    result = np.asarray(image)
    info = "runtime: %.2f ms" % (1000 * exec_time)
    cv2.putText(result, text='human detection   '+info+' AMD 3750H', org=(25, 35),fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5, color=(55, 125, 125), thickness=1)
    cv2.namedWindow("result", cv2.WINDOW_AUTOSIZE)
    result = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imshow("result", result)
    if cv2.waitKey(1) & 0xFF == ord('q'): break