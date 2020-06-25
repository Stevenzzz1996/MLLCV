#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/6/5 11:23


import keras
import tensorflow as tf
print(tf.__version__)
mnist = keras.datasets.mnist.load_data()
#print(mnist)

batch_size= 100
n_batch = mnist.train.num_examples // batch_size  # 计算一共有多少个批次

x = tf.compat.v1.placeholder(tf.float32,[None,784])  # 一张图为784列，行不确定
y = tf.compat.v1.placeholder(tf.float32,[None,10])  # 标签为0-9
keep_prob = tf.compat.v1.placeholder(tf.float32)  # dropout
lr = tf.Variable(0.001,dtype=float32)

# 创建一个神经网络
w1 = tf.Variable(tf.random.truncated_normal([784,500],stddev=0.1))
b1 = tf.Variable(tf.zeros([500]) + 0.1)
l1 = tf.nn.tanh(tf.matmul(x,W1)+b1)
l1_drop = tf.nn.dropout(l1,keep_prob)


w2 = tf.Variable(tf.random.truncated_normal([500,300],stddev=0.1))
b2 = tf .Variable(tf.zeros([300]) + 0.1)
l2 = tf.nn.tanh(tf.matmul(l1_drop,W2) + b2)
l2_drop = tf.nn.dropout(l2, keep_prob)

w3 = tf.Variable(tf.random.truncated_normal([300,10],stddev=0.1))
b3 = tf .Variable(tf.zeros([10]) + 0.1)
prediction = tf.nn.softmax(tf.matmul(l2_drop,w3) +b3)

# 交叉熵损失
loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y,
                                                              logits=prediction))
# 采用adam自适应优化器
optimizer = tf.train.AdamOptimizer(lr)
# 最小化损失函数
train_step = optimizer.minimize(loss)
# 初始化
init = tf.global_variables_initializer()
# 求准确率方法，将结果存放在一个布尔型列表中
correct_prediction = tf.equal(tf.argmax(y,1),tf.argmax(prediction,1))
#求准确率
accuracy = tf.reduce_mean(tf.cast(correct_prediction,tf.float32))

with tf.compat.v1.Session() as sess:
    sess.run(init)
    for epoch in range(51):
        sess.run(tf.compat.v1.assign(lr,0.001 ** epoch))
        for batch in range(n_batch):
            batch_xs,batch_ys = mnist.train.next_batch(batch_size)
            sess.run(train_step,feed_dict={x:batch_xs, y:batch_ys,
                                           keep_prob:1.0})

        learning_rate = sess.run(lr)
        acc = sess.run(accuracy, feed_dict = {x:mnist.test.images,y:mnist.test.labels,keep_prob:1.0})

        print('iter'+str(epoch)+"testing Accuracy" + str(acc) + 'learning_rate' + str(learning_rate))