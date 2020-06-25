#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/6 10:58


def flat(nums):
    res = []
    for i in nums:
        if isinstance(i, list):
            res.extend(flat(i))
        else:
            res.append(i)
    return res

list_0 = [[1, [2]], [3, 4, 5], [6, 7], [8], [9]]

list_1 = [[1, 2], [3, 4, 5], [6, 7], [8], [9]]
list_2 = []
for i in list_1:
    list_2 += i
print(list_2)
print(flat(list_0))

# 列表推导
list_1 = [[1, 2], [3, 4, 5], [6, 7], [8], [9]]
list_2 = [i for k in list_1 for i in k]
print(list_2)