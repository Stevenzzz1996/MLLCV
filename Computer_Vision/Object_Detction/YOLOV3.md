#                            ![](C:\Users\24991\Desktop\3e971993f41dcaa6f21c5a286f3af6a1.jpg)              ---------------------Object Detection---------------------

作者:孟令龙                                                                                                                                             实习导师：李科健

---

## 									                                     One-stage算法分析
## 原理分析

***

**YOLOV3是常见的目标检测算法，速度快，精准度还是不错，是值得我们深入的探讨baseline**

### 检测结构包含

* **backbone**残差结构的darknet53
* FPN的三种模式的设计
* Loss设计

* NMS/K-Means/IOU

* <img src="C:\Users\24991\Desktop\v3.jpg" style="zoom:80%;" />
***

#### 骨干网络 **backbone**

1.残差网络到底有什么好处，他在解决一个什么问题，为什么会显著性提升yolo的性能？？我们还可以如何改进？？

***

1.信息流失

2.非线性

3.梯度消失爆炸

[resnet](https://zhuanlan.zhihu.com/p/42706477)

![](C:\Users\24991\Desktop\resnet.jpg)

### **Head**（大中小三种尺度预测解决了什么问题，结合常用的attention机制如何进行感受野模块的设计？）

***

在NIPS2016的有关于感受野的文章中我们可以知道是，3*3的卷积的感受野比较有限，但是如果我们在一个小的feature map中3×3的感受野就会变得比较大，在一个大的feature map中3×3的感受野就比较小，从这个角度来说，为了解决不同尺度目标检测的问题，YOLOV3就采用这样分离感知的设计。

**跳层结构**我们在Resnet、Unet++、DenseNet这一系列网络中了解到了，减少CNN在特征提取中的信息流失。这种方法特别类似于我们控制系统中的闭环控制，起到一种参数调整以及高层信息与底层信息互通的效果。

针对这样的情况YOLOV3就采取了这样的设计，我们回顾文章你就会知道v3版本的YOLO仅仅是一个baseline，如果我们要提升准确度，还可以根据这两点增加不同的模块设计。

[https://zhuanlan.zhihu.com/p/42706477]:

---

### 聚合感知和分离感知对于视觉任务的一种启示

​		FPN结构这种思路已经在2015年的Unet中使用，现在已经被广泛应用于目标检测中。现今为止，Unet网络结构也是非常重要的baseline，在医疗图像和缺陷分割应用甚多。在语义分割中我们经常了解到聚合感受野模块对于语义分割网络的提升，如：ASPP、Attention，后续的研究人员在感受野分析过程中也表明了这些聚合感知模块能够极大的提升网络的感受野，所以后续文章有很多针对于这方面的东西出现，如：dense_deeplab、rbf、asff。对现有的聚合感知模块增加或者优化，提升网络的预测性能已经是一种必不可少的趋势。作为非常好的baseline的yolov3也是如此，只要在三个分离的head中加入空间空洞卷积就能让他有不少的提升。

​		目前来说，语义分割中针对的数据集都是以自动驾驶的cityscapes为主，大部分的baseline也是基于这个数据集进行相关的设计，cityscapes数据集中很多语义分割网络通常会遇到感受野不够大的问题，如：一个巴士可能占据图片的百分之七十，巴士中有很多镜面的反射，这些反射可能是人可能是街景。如果我们的网络设计感受野不够大，就非常容易出现歧义的问题。

​		当然，过分关注一个问题，就容易忽略其他的问题。

​		实际过程中我们遇到的视觉问题往往是千变万化的，如果我们感受野需求比较小，我们强行加入聚合感受野模块，对准确度提升不是很大，也会降低网络的速度。

​		结合YOLO分离设计，我们可以引入这样的思考：可以采用分离感知的方法处理图像分割中确定的大中小目标分割问题呢？我想这应该是一个非常好的idea。

​		当然感受野设计是非常重要，也是非常学术的问题，需要后续周密的实验数据来支撑这一个想法。

***

### LOSS设计：减小网络的回归任务

​		先验数据非常的重要，传统的图像特征提取设计，往往结合了视觉任务中很多的先验知识。深度学习的来临，很大程度我们弱化了先验知识的重要性，但是不管神经网络拟合能力多么的强大，泛化性多么的厉害，基于先验知识去设计网络往往都是视觉中的不二法门。

​		初看YOLOv3的时候，我不得不为它巧妙的设计折服，预测边框坐标，实际来说是一个回归问题。用CNN来直接回归预测非常难收敛，先验框的引入，把网络loss可以压缩到一个非常小的范围，网络只需要选取合适的先验框就能够极大减小回归的难度，能够对训练收敛和预测性能有非常大的提升。

 *coco--datasets：feature_map+先验框个数(3)+（边框坐标(x,y,w,h)+边框置信度()+分类种类(channel)）索引最终输出(x,y) (w,h) classfication identification*

[https://zhuanlan.zhihu.com/p/94799295]: 目标检测各种loss解释

#### 关于那些解决回归的IOU loss：





***

### 几个基础问题：K-means聚类、IOU、NMS

#### k-Means

#### IOU

#### NMS

***

### training details

1.数据增强（裁剪、翻转）

2.自动学习率下降

3.每周期检测一次map

---

# 							                       Split YOLO Expriments

---

归一化：

激活函数：

聚合感知模块：

LOSS:

BACKBONE:

---



简易化目标检测过程中的一些核心的问题。

整体来说：

​                                                                     image 和 label 进入到程序中

1.image在比例不变的情况下，缩小至416*416

2.label要根据聚类的anchor结果分出large_bbox、middle_bbox、small_bbox。这三个bouding_box 也要根据相应的head和anchor大小变成（gx,gy,gw,gh）这样主要也是为了计算loss。yolov3的loss主要是计算x相对于的feature_map的offsets、y相对于feature_map的offsets、w相对于anchor的缩放、h相对于anchor的缩放、预测框的置信度、预测种类的概率值，所有的值都要处理成为0~1。

3.数据处理好即送入到backbone。（backbone有三个head分别是downsampling stride = 8、16、32）针对backbone我们可以加入适当的模块如：ASPP、Self_Attention、RFB、ASFF、PAM模块利用聚合感知增大网络感受野范围，当然我们也可以用Houghlass、Xception、Mobilenet、Resnet利用不同的backbone去trade off速度与准度。

4.数据输出同label计算loss完成后，这样训练即结束了。在训练过程中我们可以手动或者自动都可以调节学习率，以达到更好的训练效果。

5.如果数据比较的少量，做数据增强是非常有必要，数据增强主要是做图像裁剪、翻转。根据实际的任务可以有不同的增强方式。

6.其他的方式有效的yoloV4的作者已经做了充分的消融实验。比如BN、Activation layer改动（各种版本的relu、swish、mish等）

-----

#### part1:

base_experiments

整体实现流程：

数据：

---

#### part2：聚合感知和分离感知影响

(聚合感知模块：asff、aspp、self_attention、RFB)

整体实现流程：

数据：

---

#### part3：backbone影响（Mobilenet、Xception、Resnet、Darknet、SE_module）

整体实现流程：

数据：

---

#### part4：部件影响（BN series、Downsampling、Activation）

整体实现流程：

数据：

---

#### Other ways ：anchor base



---

#### part5：优化部件： nms soft-nms

整体实现流程：

数据：

----

part6：

### LOSS优化：

Focal_LOSS、GIOU_LOSS、 DIOU_LOSS、 CIOU_LOSS

整体实现流程：

数据：

---

## 整体代码、技术报告地址：

#### refenrence:

​	










