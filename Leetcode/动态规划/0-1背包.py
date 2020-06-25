#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/26 10:48


import numpy as np
weight = [2,2,6,5,4]
value = [3,6,5,4,6]
weight_most = 10
def bag_0_1(weight,value,weight_most):  # return max value
    weight.insert(0, 0)
    value.insert(0, 0)
    bag = [[0]*(weight_most+1) for _ in range(len(weight))]
    # bag = np.zeros((len(weight),weight_most+1), dtype=np.int32)
    for i in range(1, len(weight)):  # 插入了一个0之后，长度已经加1了。不许再加了！
        for j in range(1, weight_most+1):
            if weight[i] <= j:
                bag[i][j] = max(bag[i-1][j-weight[i]]+value[i], bag[i-1][j])
            else:
                bag[i][j] = bag[i-1][j]
    return bag[-1][-1]

# def bag_print(weight, value, weight_most):
#     # return max value
#     weight.insert(0, 0)
#     value.insert(0, 0)
#     bag = [[0]*(weight_most+1) for _ in range(len(weight))]
#     # bag = np.zeros((len(weight),weight_most+1), dtype=np.int32)
#     for i in range(1, len(weight)):  # 插入了一个0之后
#         for j in range(1, weight_most+1):
#             if weight[i] <= j:
#                 bag[i][j] = max(bag[i-1][j-weight[i]]+value[i], bag[i-1][j])
#             else:
#                 bag[i][j] = bag[i-1][j]
#
#     return bag  # 查看bag


print(bag_0_1(weight, value, weight_most))

print(bag_print(weight, value, weight_most))

# [[ 0  0  0  0  0  0  0  0  0  0  0]
#  [ 0  0  3  3  3  3  3  3  3  3  3]
#  [ 0  0  6  6  9  9  9  9  9  9  9]
#  [ 0  0  6  6  9  9  9  9 11 11 14]
#  [ 0  0  6  6  9  9  9 10 11 13 14]
#  [ 0  0  6  6  9  9 12 12 15 15 15]]