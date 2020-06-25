#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/15 11:18

# 初始数据：每个样本是列表的一个元素（本例中的样本是一个句子，但也可以是一整篇文档）
# import numpy as np
# import os
#
# samples = [' The cat sat on the mat.', ' The dog ate my homework.']
# token_idx = {}  # 构建数据中所有标记的索引
# for sample in samples:
#     for word in sample.split():
#         if word not in token_idx:
#             token_idx[word] = len(token_idx)+1
# max_length = 10
# res = np.zeros(shape=(len(samples), max_length, max(token_idx.values()) + 1))  # (最后代表个数，2，10，11)
# for i, sample in enumerate(samples):
#     for j, word in list(enumerate(sample.split()))[:max_length]:
#         index = token_idx.get(word)
#         res = [i, j, index] = 1.
#
# # 字符级别的one-hot简单举例
# import string
# samples=['The cat sat on the mat.', 'The dog ate my homework.']
# characters=string.printable
# token_index=dict(zip(range(1,len(characters)+1),characters))
# max_length=50
# res = np.zeros((len(samples), max_length, max(token_idx.keys()) + 1))
# for i, sample in enumerate(samples):
#     for j, character in enumerate(sample): # 所有可打印的ASCll字符
#         index = token_index.get(character)
#         res[i, j, index] = 1.

from keras.preprocessing.text import Tokenizer
samples = ['The cat sat on the mat.', 'The dog ate my homework.']
tokenizer = Tokenizer(num_words=1000)
tokenizer.fit_on_texts(samples)  # 构建单词索引
sequences = tokenizer.texts_to_sequences(samples)  # 将字符串转换为整数索引组成的列表
one_hot_results = tokenizer.texts_to_matrix(samples, mode="binary")
word_index = tokenizer.wrod_index  # 找回单词索引
print("Found %s unique tokens" % len(word_index))
