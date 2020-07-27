import tensorflow as tf
from core.resnet_yolohead import resnet_18, resnet_34, resnet_50, resnet_101, resnet_152
import numpy as np
from core.utils import get_anchors
import tensorflow_addons as tfa

'''
    试验性代码
'''

NUM_CLASS = 1
STRIDES = [8, 16, 32]
ANCHORS = np.array(get_anchors('C:/Users/24991/Desktop/YOLOV3/data/anchors/basline_anchors.txt'))

def decode(conv_output, i=0):
    """
    return tensor of shape [batch_size, output_size, output_size, anchor_per_scale, 5 + num_classes]
            contains (x, y, w, h, score, probability)
    """

    conv_shape = tf.shape(conv_output)
    batch_size = conv_shape[0]
    output_size = conv_shape[1]

    conv_output = tf.reshape(conv_output, (batch_size, output_size, output_size, 3, 5 + NUM_CLASS))

    conv_raw_dxdy = conv_output[:, :, :, :, 0:2]
    conv_raw_dwdh = conv_output[:, :, :, :, 2:4]
    conv_raw_conf = conv_output[:, :, :, :, 4:5]
    conv_raw_prob = conv_output[:, :, :, :, 5:]

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


class ASPP(tf.keras.Model):
    def __init__(self, fitler_nums):
        super(ASPP, self).__init__()
        self.dconv1 = tf.keras.layers.Conv2D(filters=fitler_nums,
                                             kernel_size=(3, 3),
                                             strides=1,
                                             dilation_rate=1,
                                             padding="same")
        self.dconv2 = tf.keras.layers.Conv2D(filters=fitler_nums,
                                             dilation_rate=6,
                                             kernel_size=(3, 3),
                                             strides=1,
                                             padding="same")
        self.dconv3 = tf.keras.layers.Conv2D(filters=fitler_nums,
                                             dilation_rate=12,
                                             kernel_size=(3, 3),
                                             strides=1,
                                             padding="same")
        self.dconv4 = tf.keras.layers.Conv2D(filters=fitler_nums,
                                             kernel_size=(3, 3),
                                             dilation_rate=18,
                                             strides=1,
                                             padding="same")
        self.avg = tf.keras.layers.AveragePooling2D(pool_size=2, strides=1, padding='same')

    def call(self, inputs, training=None, mask=None):
        x1 = self.dconv1(inputs)
        x2 = self.dconv2(inputs)
        x3 = self.dconv3(inputs)
        x4 = self.dconv4(inputs)
        x5 = self.avg(inputs)
        output = tf.concat([x1, x2, x3, x4, x5], axis=-1)
        return output


# class mish(tf.keras.Model):
class DBL(tf.keras.layers.Layer):
    def __init__(self, fitler_nums):
        super(DBL, self).__init__()
        self.conv1 = tf.keras.layers.Conv2D(filters=fitler_nums,
                                            kernel_size=(3, 3),
                                            strides=1,
                                            padding="same")
        self.bn = tf.keras.layers.BatchNormalization()

    def call(self, inputs, training=None, mask=None):
        x = self.conv1(inputs)
        x = self.bn(x, training=training)
        x = tf.nn.leaky_relu(x)
        return x


'''
define model use tf 2.0 
'''
def mish(x):
    return tfa.activations.mish(x)

class spp(tf.keras.Model):
    def __init__(self):
        super(spp, self).__init__()
        self.pool1 = tf.keras.layers.MaxPooling2D((5, 5), strides=1, padding='same')
        self.pool2 = tf.keras.layers.MaxPooling2D((9, 9), strides=1, padding='same')
        self.pool3 = tf.keras.layers.MaxPooling2D((13, 13), strides=1, padding='same')

    def call(self, x):
        return tf.concat([self.pool1(x), self.pool2(x), self.pool3(x), x], -1)

class LLYOLO(tf.keras.Model):
    def __init__(self):
        super(LLYOLO, self).__init__()
        self.backbone = resnet_18()
        self.DBL512_1 = DBL(512)
        self.DBL512_2 = DBL(512)
        self.DBL256_1 = DBL(256)
        self.DBL256_2 = DBL(256)
        self.DBL128_1 = DBL(128)
        self.DBL128_2 = DBL(128)
        self.DBL128_3 = DBL(128)

        self.DBL512_3 = DBL(512)
        self.DBL512_4 = DBL(512)
        self.DBL256_3 = DBL(256)
        self.DBL256_4 = DBL(256)
        self.DBL128_4 = DBL(128)
        self.DBL128_5 = DBL(128)
        self.DBL128_6 = DBL(128)

        self.convoutput1 = tf.keras.layers.Conv2D(filters=3 * (5 + NUM_CLASS),
                                                  kernel_size=(1, 1),
                                                  strides=1,
                                                  padding="same")
        self.convoutput2 = tf.keras.layers.Conv2D(filters=3 * (5 + NUM_CLASS),
                                                  kernel_size=(1, 1),
                                                  strides=1,
                                                  padding="same")
        self.convoutput3 = tf.keras.layers.Conv2D(filters=3 * (5 + NUM_CLASS),
                                                  kernel_size=(1, 1),
                                                  strides=1,
                                                  padding="same")
        self.up2x = tf.keras.layers.UpSampling2D(size=(2, 2))
        self.ASPP1 = ASPP(fitler_nums=56)
        self.ASPP2 = ASPP(fitler_nums=128)
        self.ASPP3 = ASPP(fitler_nums=256)

        self.ASPP4 = ASPP(fitler_nums=56)
        self.ASPP5 = ASPP(fitler_nums=128)
        self.ASPP6 = ASPP(fitler_nums=256)

        self.ASPP7 = ASPP(fitler_nums=56)
        self.ASPP8 = ASPP(fitler_nums=128)
        self.ASPP9 = ASPP(fitler_nums=256)

    def call(self, inputs, training=None, mask=None):
        feature_map1, feature_map2, feature_map3 = self.backbone(inputs)
        feature_map1_aspp = self.ASPP1(feature_map1)
        feature_map2_aspp = self.ASPP2(feature_map2)
        feature_map3_aspp = self.ASPP3(feature_map3)
        # print(feature_map1.shape, feature_map2.shape, feature_map3.shape)
        feature_map3 = self.DBL512_1(feature_map3_aspp)

        concat_featuremap2 = self.up2x(feature_map3)  # [512,26,26,3]

        feature_map2 = self.DBL512_2(feature_map2_aspp)
        feature_map2 = tf.concat([concat_featuremap2, feature_map2], axis=3)
        feature_map2 = self.DBL256_1(feature_map2)

        concat_featuremap1 = self.up2x(feature_map2)
        concat_featuremap1 = self.DBL256_2(concat_featuremap1)
        feature_map1 = tf.concat([concat_featuremap1, feature_map1_aspp], axis=3)

        feature_map1 = self.DBL128_1(feature_map1)
        feature_map2 = self.DBL128_2(feature_map2)
        feature_map3 = self.DBL128_3(feature_map3)

        # 第二层fpn+aspp设计
        feature_map1 = self.ASPP4(feature_map1)
        feature_map2 = self.ASPP5(feature_map2)
        feature_map3 = self.ASPP6(feature_map3)

        # 高层信息变大设计，底层经过两个512DBL放大，中层经过两个256DBL，大层经过两个128DBL
        concat_featuremap_small = self.DBL512_3(feature_map3)
        concat_featuremap_small_node = self.DBL512_4(concat_featuremap_small)
        concat_featuremap_small = self.up2x(concat_featuremap_small)

        concat_featuremap_mid = tf.concat([concat_featuremap_small, feature_map2], axis=-1)

        concat_featuremap_mid = self.DBL256_3(concat_featuremap_mid)
        concat_featuremap_mid_node = self.DBL256_4(concat_featuremap_mid)
        concat_featuremap_mid = self.up2x(concat_featuremap_mid_node)

        concat_featuremap_big = tf.concat([concat_featuremap_mid, feature_map1], axis=-1)

        concat_featuremap_big = self.DBL128_4(concat_featuremap_big)
        concat_featuremap_big = self.DBL128_5(concat_featuremap_big)
        concat_featuremap_big_node = self.DBL128_6(concat_featuremap_big)

        out_feature_map3 = self.ASPP9(concat_featuremap_small_node)
        out_feature_map2 = self.ASPP8(concat_featuremap_mid_node)
        out_feature_map1 = self.ASPP7(concat_featuremap_big_node)

        out_feature_map1 = tf.keras.layers.add([out_feature_map1, feature_map1_aspp])
        out_feature_map2 = tf.keras.layers.add([out_feature_map2, feature_map2_aspp])
        out_feature_map3 = tf.keras.layers.add([out_feature_map3, feature_map3_aspp])

        feature_map1 = self.convoutput1(out_feature_map1)
        feature_map2 = self.convoutput2(out_feature_map2)
        feature_map3 = self.convoutput3(out_feature_map3)
        conv_tensors = [feature_map1, feature_map2, feature_map3]
        output_tensors = []
        for i, conv_tensor in enumerate(conv_tensors):
            pred_tensor = decode(conv_tensor, i)
            output_tensors.append(conv_tensor)
            output_tensors.append(pred_tensor)

        return output_tensors

# model = YOLO()
# model.build(input_shape=(None, 416, 416, 3))
# model.summary()
