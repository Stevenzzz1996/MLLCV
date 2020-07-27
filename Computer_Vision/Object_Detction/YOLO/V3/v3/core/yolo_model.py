import tensorflow as tf
from core.resnet_yolohead import resnet_18,resnet_34,resnet_50,resnet_101,resnet_152
import numpy as np
from core.utils import get_anchors
from core.mobilenetv3 import MobileNetV3Large

NUM_CLASS = 1
STRIDES = [8, 16, 32]
ANCHORS = get_anchors('C:/Users/24991/Desktop/YOLOV3/data/anchors/basline_anchors.txt')

def decode(conv_output, i=0):
    """
    return tensor of shape [batch_size, output_size, output_size, anchor_per_scale, 5 + num_classes]
            contains (x, y, w, h, score, probability)
    """

    conv_shape       = tf.shape(conv_output)
    batch_size       = conv_shape[0]
    output_size      = conv_shape[1]

    conv_output = tf.reshape(conv_output, (batch_size, output_size, output_size, 3, 5 + NUM_CLASS))

    conv_raw_dxdy = conv_output[:, :, :, :, 0:2]
    conv_raw_dwdh = conv_output[:, :, :, :, 2:4]
    conv_raw_conf = conv_output[:, :, :, :, 4:5]
    conv_raw_prob = conv_output[:, :, :, :, 5: ]

    y = tf.tile(tf.range(output_size, dtype=tf.int32)[:, tf.newaxis], [1, output_size])
    x = tf.tile(tf.range(output_size, dtype=tf.int32)[tf.newaxis, :], [output_size, 1])

    xy_grid = tf.concat([x[:, :, tf.newaxis], y[:, :, tf.newaxis]], axis=-1)
    xy_grid = tf.tile(xy_grid[tf.newaxis, :, :, tf.newaxis, :], [batch_size, 1, 1, 3, 1])
    xy_grid = tf.cast(xy_grid, tf.float32)

    pred_xy = (tf.sigmoid(conv_raw_dxdy) + xy_grid) * STRIDES[i]
    pred_wh = (tf.exp(conv_raw_dwdh) * ANCHORS[i]) * STRIDES[i]
    pred_xywh = tf.concat([pred_xy, pred_wh], axis=-1)

    pred_conf = tf.sigmoid(conv_raw_conf)
    pred_prob = tf.sigmoid(conv_raw_prob)

    return tf.concat([pred_xywh, pred_conf, pred_prob], axis=-1)

# TODO: class ASPP(tf.keras.Model):

# TODO: class mish(tf.keras.Model):

class DBL(tf.keras.layers.Layer):
    def __init__(self,fitler_nums):
        super(DBL,self).__init__()
        self.conv1 = tf.keras.layers.Conv2D(filters=fitler_nums,
                                            kernel_size=(3, 3),
                                            strides=1,
                                            padding="same")
        self.bn = tf.keras.layers.BatchNormalization()

    def call(self, inputs, training=None, mask=None):
        x = self.conv1(inputs)
        x = self.bn(x,training=training)
        x = tf.nn.leaky_relu(x)
        return x

class YOLO(tf.keras.Model):
    '''
    define model use tf 2.0 
    '''
    def __init__(self):
        super(YOLO, self).__init__()
        self.backbone= MobileNetV3Large() # 骨干网络设计
        self.conv1 = tf.keras.layers.Conv2D(filters=512,
                                             kernel_size=(1, 1),
                                             strides=1,
                                             dilation_rate=1,
                                             padding="same")
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.conv2 = tf.keras.layers.Conv2D(filters=512,
                                             dilation_rate=1,
                                             kernel_size=(1, 1),
                                             strides=1,
                                             padding="same")
        self.bn2 = tf.keras.layers.BatchNormalization()
        self.conv3 = tf.keras.layers.Conv2D(filters=512,
                                             dilation_rate=1,
                                             kernel_size=(1, 1),
                                             strides=1,
                                             padding="same")
        self.bn3 = tf.keras.layers.BatchNormalization()
        self.DBL512_1 = DBL(512)
        self.DBL512_2 = DBL(512)
        self.DBL256_1 = DBL(256)
        self.DBL256_2 = DBL(256)
        self.DBL128_1 = DBL(128)
        self.DBL128_2 = DBL(128)
        self.DBL128_3 = DBL(128)

        self.convoutput1 = tf.keras.layers.Conv2D(filters=3*(5+NUM_CLASS),
                                            kernel_size=(3, 3),
                                            strides=1,
                                            padding="same")
        self.convoutput2 = tf.keras.layers.Conv2D(filters=3 * (5 + NUM_CLASS),
                                                 kernel_size=(3, 3),
                                                 strides=1,
                                                 padding="same")
        self.convoutput3 = tf.keras.layers.Conv2D(filters=3 * (5 + NUM_CLASS),
                                                 kernel_size=(3, 3),
                                                 strides=1,
                                                 padding="same")
        # self.up2x = tf.keras.layers.UpSampling2D(size=(2, 2))
        self._set_inputs(tf.TensorSpec([None, 416,416, 3], tf.float32, name="inputs"))

    @tf.function()
    def call(self, inputs, training=None, mask=None):
        feature_map1,feature_map2,feature_map3 = self.backbone(inputs)
        #print(feature_map1.shape,feature_map2.shape,feature_map3.shape)
        feature_map1 = self.conv1(feature_map1)
        feature_map1 = self.bn1(feature_map1)
        feature_map1 = tf.nn.leaky_relu(feature_map1)
        feature_map2 = self.conv2(feature_map2)
        feature_map2 = self.bn2(feature_map2)
        feature_map2 = tf.nn.leaky_relu(feature_map2)
        feature_map3 = self.conv3(feature_map3)
        feature_map3 = self.bn3(feature_map3)
        feature_map3 = tf.nn.leaky_relu(feature_map3)
        feature_map3 = self.DBL512_1(feature_map3)

        concat_featuremap2 = tf.keras.layers.UpSampling2D(size=(2,2))(feature_map3)  # [512,26,26,3]

        feature_map2 = self.DBL512_2(feature_map2)
        feature_map2 = tf.concat([concat_featuremap2,feature_map2],axis=3)
        feature_map2 = self.DBL256_1(feature_map2)

        concat_featuremap1 = tf.keras.layers.UpSampling2D(size=(2,2))(feature_map2)
        concat_featuremap1 = self.DBL256_2(concat_featuremap1)
        feature_map1 = tf.concat([concat_featuremap1,feature_map1],axis=3)

        feature_map1 = self.DBL128_1(feature_map1)
        feature_map2 = self.DBL128_2(feature_map2)
        feature_map3 = self.DBL128_3(feature_map3)

        feature_map1 = self.convoutput1(feature_map1)
        feature_map2 = self.convoutput2(feature_map2)
        feature_map3 = self.convoutput3(feature_map3)

        #print(feature_map1.shape,feature_map2.shape,feature_map3.shape)
        conv_tensors = [feature_map1, feature_map2, feature_map3]
        output_tensors = []
        for i, conv_tensor in enumerate(conv_tensors):
            pred_tensor = decode(conv_tensor, i)
            output_tensors.append(conv_tensor)
            output_tensors.append(pred_tensor)

        return output_tensors

model = YOLO()
model.build(input_shape=(None,416,416,3))
model.summary()