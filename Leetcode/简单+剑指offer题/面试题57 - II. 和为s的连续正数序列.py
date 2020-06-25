#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 17:50


# 双指针
def findContinueSequence(target):
    i = j = 1   # j往前走，i用于从前面截断
    cur_sum = 0
    res = []
    while j < target:  # j小于target的都有可能
        # 内循环操作
        cur_sum += j  # 依次加
        j += 1
        while cur_sum > target:  # 太大了就依次剪掉i
            cur_sum -= i
            i += 1
        if cur_sum == target:   # 相等了就加进来！
            res.append(list(range(i, j)))
    return res
print(findContinueSequence(target = 9))