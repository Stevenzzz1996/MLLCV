#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/27 21:39


n, v = map(int, input().split())
goods = []
for i in range(n):
    goods.append([int(i) for i in input().split()])
dp = [0 for i in range(v+1)]
for i in range(n):
    for j in range(v+1): # 从前往后
        if j >= goods[i][0]:
            dp[j] = max(dp[j], dp[j-goods[i][0]]+goods[i][1])


print(dp[-1])

# # 物品的重量和价值
# weights = [5, 4, 7, 2, 6]
# values = [12, 3, 10, 3, 6]
# # 背包容量
# Capacity = 15
#
# # 0&1背包方案
# res = [0]*16
# for i in range(len(weights)):
#     for j in range(len(res)-1, -1, -1):
#         if j >= weights[i]:
#             res[j] = max(res[j], max(res[j - 1], res[j - weights[i]] + values[i]))
#
# print(res)
# # 完全背包方案
# res = [0]*16
# for c in range(0, Capacity+1):
#     for i, weight in enumerate(weights):
#         if c >= weight:
#             res[c] = max(res[c], max(res[c-1], (res[c - weight] + values[i])))
# print(res)
#
# # 多重背包问题
# Capacity = 9
# weights = [2, 4]
# values = [100, 300]
# counts = [4, 1]
# res = [0] * (Capacity+1)
# for i in range(len(weights)):   # 物品种类
#     for c in range(counts[i]):  # 物品个数
#         for j in range(len(res)-1, -1, -1):  # 包空间
#             if j >= weights[i]:
#                 res[j] = max(res[j], max(res[j - 1], res[j - weights[i]] + values[i]))
# print(res)
