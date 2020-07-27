import tensorflow as tf
'''
    模型放置于移动端的目标检测
    特点有2:
        1，适配移动端模型部署与预测
        2，新增聚合感知模块
'''

def h_sigmoid(x):
    return tf.nn.relu6(x + 3) / 6

def h_swish(x):
    return x * h_sigmoid(x)

class SEBlock(tf.keras.layers.Layer):
    def __init__(self, input_channels, r=16):
        super(SEBlock, self).__init__()
        self.pool = tf.keras.layers.GlobalAveragePooling2D()
        self.fc1 = tf.keras.layers.Dense(units=input_channels // r)
        self.fc2 = tf.keras.layers.Dense(units=input_channels)

    def call(self, inputs, **kwargs):
        branch = self.pool(inputs)
        branch = self.fc1(branch)
        branch = tf.nn.relu(branch)
        branch = self.fc2(branch)
        branch = h_sigmoid(branch)
        branch = tf.expand_dims(input=branch, axis=1)
        branch = tf.expand_dims(input=branch, axis=1)
        output = inputs * branch
        return output

class BottleNeck(tf.keras.layers.Layer):
    def __init__(self, in_size, exp_size, out_size, s, is_se_existing, NL, k):
        super(BottleNeck, self).__init__()
        self.stride = s
        self.in_size = in_size
        self.out_size = out_size
        self.is_se_existing = is_se_existing
        self.NL = NL
        self.conv1 = tf.keras.layers.Conv2D(filters=exp_size,
                                            kernel_size=(1, 1),
                                            strides=1,
                                            padding="same")
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.dwconv = tf.keras.layers.DepthwiseConv2D(kernel_size=(k, k),
                                                      strides=s,
                                                      padding="same")
        self.bn2 = tf.keras.layers.BatchNormalization()
        self.se = SEBlock(input_channels=exp_size)
        self.conv2 = tf.keras.layers.Conv2D(filters=out_size,
                                            kernel_size=(1, 1),
                                            strides=1,
                                            padding="same")
        self.bn3 = tf.keras.layers.BatchNormalization()
        self.linear = tf.keras.layers.Activation(tf.keras.activations.linear)

    def call(self, inputs, training=None, **kwargs):
        x = self.conv1(inputs)
        x = self.bn1(x, training=training)
        if self.NL == "HS":
            x = h_swish(x)
        elif self.NL == "RE":
            x = tf.nn.relu6(x)
        x = self.dwconv(x)
        x = self.bn2(x, training=training)
        if self.NL == "HS":
            x = h_swish(x)
        elif self.NL == "RE":
            x = tf.nn.relu6(x)
        if self.is_se_existing:
            x = self.se(x)
        x = self.conv2(x)
        x = self.bn3(x, training=training)
        x = self.linear(x)

        if self.stride == 1 and self.in_size == self.out_size:
            x = tf.keras.layers.add([x, inputs])

        return x

class RASPP(tf.keras.Model):
    '''
        proposed alg: RASPP
        based alg: TODO: ADD Link
                    deeplabv3+ paper:https://arxiv.org/pdf/1802.02611.pdf
                    resnet          :https://zhuanlan.zhihu.com/p/42706477
                    resnet paper    :https://arxiv.org/abs/1512.03385
        innovaton points:
            1. TODO: 加入1残差模块，由算法resnet的residual思想演变而来 y = h(x1)+F(x1,w),x2 = f(y),当反向梯度传播时求
                    导时不会有梯度消失的现象.在前向传输的过程中，随着层数的加深，Feature Map包含的图像信息会逐层减少，
                    而ResNet的直接映射的加入，保证了l+1层的网络一定比l层包含更多的图像信息。这样的想法使得ASPP模块更加稳定给网络
                    带来收益。
            2. TODO: 加入聚合感知模块 ASPP,经文献研究我们可知，底层的feature map有着丰富的语义以及位置信息对于模型的预测
                     非常重要,在底层加入ASPP模块能够有效增强感受野能力从而捕获到这些语义以及位置信息。传统的3*3卷积受限于尺寸
                     的影响无法捕获更大的感受野，而传统的7*7或者更大的卷积会让模型参数增多并且变慢，空间空洞卷积能够有效的提升
                     模型感受野，并且使得模型速度不会变慢太多，同时使得模型能够对大中小的物体具有感知的能力。
        exp results:
            1. TODO ：
                    coco person map =
                    runtime         = 270ms in AMD 3750 CPU /cc ms in Nvidia RTX2080ti /xx ms in Nvidia  RTX2070

    '''
    def __init__(self,fitler_nums):
        super(RASPP,self).__init__()
        self.dconv1 = tf.keras.layers.Conv2D(filters=fitler_nums,
                                            kernel_size=(1, 1),
                                            strides=1,
                                            dilation_rate = 1,
                                            padding="same")
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.dconv2 = tf.keras.layers.Conv2D(filters=fitler_nums,
                                            dilation_rate = 6,
                                            kernel_size=(3, 3),
                                            strides=1,
                                            padding="same")
        self.bn2 = tf.keras.layers.BatchNormalization()
        self.dconv3 = tf.keras.layers.Conv2D(filters=fitler_nums,
                                            dilation_rate = 12,
                                            kernel_size=(3, 3),
                                            strides=1,
                                            padding="same")
        self.bn3 = tf.keras.layers.BatchNormalization()
        self.dconv4 = tf.keras.layers.Conv2D(filters=fitler_nums,
                                            dilation_rate=18,
                                            kernel_size=(3, 3),
                                            strides=1,
                                            padding="same")
        self.bn4 = tf.keras.layers.BatchNormalization()
        self.dconv5 = tf.keras.layers.Conv2D(filters=fitler_nums,
                                            kernel_size=(1, 1),
                                            dilation_rate = 1,
                                            strides=1,
                                            padding="same")
        self.bn5 = tf.keras.layers.BatchNormalization()
        self.dconv6 = tf.keras.layers.Conv2D(filters=fitler_nums*5,
                                             kernel_size=(1, 1),
                                             dilation_rate=1,
                                             strides=1,
                                             padding="same")
        self.bn6 = tf.keras.layers.BatchNormalization()
        self.avg = tf.keras.layers.AveragePooling2D(pool_size=2, strides=1, padding='same')

    def call(self, inputs, training=None, mask=None):
        x1 = self.dconv1(inputs)
        x1 = self.bn1(x1)
        x1 = tf.nn.leaky_relu(x1)
        x2 = self.dconv2(inputs)
        x2 = self.bn2(x2)
        x2 = tf.nn.leaky_relu(x2)
        x3 = self.dconv3(inputs)
        x3 = self.bn3(x3)
        x3 = tf.nn.leaky_relu(x3)
        x4 = self.dconv4(inputs)
        x4 = self.bn4(x4)
        x4 = tf.nn.leaky_relu(x4)
        x5 = self.dconv5(inputs)
        x5 = self.bn5(x5)
        x5 = tf.nn.leaky_relu(x5)
        x5 = self.avg(x5)
        x6 = self.dconv6(inputs)
        x6 = self.bn6(x6)
        x6 = tf.nn.leaky_relu(x6)
        output = tf.concat([x1, x2, x3, x4, x5],axis=-1)
        output = tf.keras.layers.add([x6,output])
        return output

class MobileNetV3Large(tf.keras.Model):
    def __init__(self):
        super(MobileNetV3Large, self).__init__()
        self.conv1 = tf.keras.layers.Conv2D(filters=16,
                                            kernel_size=(3, 3),
                                            strides=2,
                                            padding="same")
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.bneck1 = BottleNeck(in_size=16, exp_size=16, out_size=16, s=1, is_se_existing=False, NL="RE", k=3)
        self.bneck2 = BottleNeck(in_size=16, exp_size=64, out_size=24, s=2, is_se_existing=False, NL="RE", k=3)
        self.bneck3 = BottleNeck(in_size=24, exp_size=72, out_size=24, s=1, is_se_existing=False, NL="RE", k=3)
        self.bneck4 = BottleNeck(in_size=24, exp_size=72, out_size=40, s=2, is_se_existing=True, NL="RE", k=5)
        self.bneck5 = BottleNeck(in_size=40, exp_size=120, out_size=40, s=1, is_se_existing=True, NL="RE", k=5)
        self.bneck6 = BottleNeck(in_size=40, exp_size=120, out_size=40, s=1, is_se_existing=True, NL="RE", k=5)
        self.bneck7 = BottleNeck(in_size=40, exp_size=240, out_size=80, s=2, is_se_existing=False, NL="HS", k=3)
        self.bneck8 = BottleNeck(in_size=80, exp_size=200, out_size=80, s=1, is_se_existing=False, NL="HS", k=3)
        self.bneck9 = BottleNeck(in_size=80, exp_size=184, out_size=80, s=1, is_se_existing=False, NL="HS", k=3)
        self.bneck10 = BottleNeck(in_size=80, exp_size=184, out_size=80, s=1, is_se_existing=False, NL="HS", k=3)
        self.bneck11 = BottleNeck(in_size=80, exp_size=480, out_size=112, s=1, is_se_existing=True, NL="HS", k=3)
        self.bneck12 = BottleNeck(in_size=112, exp_size=672, out_size=112, s=1, is_se_existing=True, NL="HS", k=3)
        self.bneck13 = BottleNeck(in_size=112, exp_size=672, out_size=160, s=2, is_se_existing=True, NL="HS", k=5)
        self.bneck14 = BottleNeck(in_size=160, exp_size=960, out_size=160, s=1, is_se_existing=True, NL="HS", k=5)
        self.bneck15 = BottleNeck(in_size=160, exp_size=960, out_size=160, s=1, is_se_existing=True, NL="HS", k=5)

        self.conv2 = tf.keras.layers.Conv2D(filters=960,
                                            kernel_size=(1, 1),
                                            strides=1,
                                            padding="same")
        self.bn2 = tf.keras.layers.BatchNormalization()

        self.raspp = RASPP(fitler_nums=128)


    def call(self, inputs, training=None, mask=None):
        x = self.conv1(inputs)
        x = self.bn1(x, training=training)
        x = h_swish(x)

        x = self.bneck1(x, training=training)
        x = self.bneck2(x, training=training)# (104)
        x = self.bneck3(x, training=training)
        stage1 = self.bneck4(x, training=training)# (52)
        x = self.bneck5(stage1, training=training)
        x = self.bneck6(x, training=training)
        stage2 = self.bneck7(x, training=training)# (26)
        x = self.bneck8(stage2, training=training)
        x = self.bneck9(x, training=training)
        x = self.bneck10(x, training=training)
        x = self.bneck11(x, training=training)
        x = self.bneck12(x, training=training)
        stage3 = self.bneck13(x, training=training)# (13)
        stage3 = self.bneck14(stage3, training=training)
        stage3 = self.bneck15(stage3, training=training)

        stage3 = self.conv2(stage3)
        stage3 = self.bn2(stage3, training=training)
        stage3 = h_swish(stage3)
        stage3 = self.raspp(stage3)
        return stage1,stage2,stage3

# model = MobileNetV3Large()
# model.build(input_shape=(None,416,416,3))
# model.summary()
# x = tf.ones(shape=(1,416,416,3))
# x1,x2,x3 = model(x)
# print(x1,x2,x3)