# YOLO Object Detection Series (TF 2.X)

1.支持权重调用以及使用

2.支持backbone更换（Resnet18、32、50、101、152 && MobileNet+RASPP）

3.支持训练保存H5 & PB 文件

4.支持PB->tflite文件，tflite文件可部署在嵌入式、移动端（ios、andorid）、服务器端等等。

TOD0:
5.完整文档后续更新,yolo原理分析、yolov4代码复现。

6.实验性代码：centernet & mobilentv3 centernet

6.添加tensorflow.pruning+tensorflow.lite实验性代码，探索剪枝和量化技术对于模型速度
、功耗、容量、精度的影响。


---
## 文档说明（如何使用本代码训练网络）
- 原理性说明
    - 如果你任务很大你可能需要改动input size 高分辨率的图像附带更多信息，可能对你的训练结果有
        很大的影响。
    - 你需要根据你的任务改动你的backbone或者neck，比如复杂的任务你可能需要resnet50、101、152
        简单任务你可能只需要mobilnet、resnet32、18就好了。

- 你需要将input 制作成txt文件。txt文件的格式为data/datasets/train2.txt
  data文件夹下面有json转换txt的py文件这个适用于coco数据集。
  train2.txt文件里面只有peson这一类原因在于本项目最初用于行人检测。显然这网络是可以适用于检测任何物体的，
  只要把num_class = class num。
        
- data文件下面放置的anhors是用于网络的先验框数据，它是由kmeans聚类而成9类。
  如果你不想改动你可以不改，他只会对你的训练产生影响，如果训练的够久，不会对结果有很大影响，当然这个过程我认为
  你最好还是做做，因为这是理解anchor base的开始。

- coco names 是放置标签的索引，用来video demo 显示调用。

- config 文件是参数设置可以设置input分辨率，数据等等，注意：这里学习率是采用warm up 自动调节学习率的方式
  你需要最好有一台多卡的机器 不然其写一个其他调节程序，因为它非常容易nan，这是由于giou产生问题。
  
- 启动train.py文件若干时间后你就可以得到H5文件，你可以使用video demo 显示你的模型的结果。


  
  
