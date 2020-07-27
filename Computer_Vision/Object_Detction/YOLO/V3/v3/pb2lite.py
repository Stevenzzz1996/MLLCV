import core.utils as utils
import tensorflow as tf
from core.yolov3 import YOLOv3, decode
from core.yolo_model import YOLO
from core.LLmodel import LLYOLO
import numpy as np
import cv2

# step1:h5 to pb
# model = YOLO()
# model.build(input_shape=(None,416,416,3))
# # model.build(input_shape=(None,416,416,3))
# model.load_weights('C:/Users/24991/Desktop/YOLOV3/small_yolo.h5')
# #model.summary()
# model.save('small_yolo')

# step2:pb to tflite
saved_model_dir = 'small_yolo'
converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS,tf.lite.OpsSet.SELECT_TF_OPS]
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_quantized_model = converter.convert()
open("converted_model.tflite", "wb").write(tflite_quantized_model)

# step3: how to inference tflite model to predict image
# interpreter = tf.lite.Interpreter(model_path="converted_model.tflite")
# interpreter.allocate_tensors()
#
# # Get input and output tensors.
# input_details = interpreter.get_input_details()
# output_details = interpreter.get_output_details()
#
# # Test the model on random input data.
# input_shape = input_details[0]['shape']
# input_data = np.array(np.random.random_sample(input_shape), dtype=np.float32)
# interpreter.set_tensor(input_details[0]['index'], input_data)
#
# interpreter.invoke()
#
# # The function `get_tensor()` returns a copy of the tensor data.
# # Use `tensor()` in order to get a pointer to the tensor.
# output_data = interpreter.get_tensor(output_details[0]['index'])
# print(output_data)

