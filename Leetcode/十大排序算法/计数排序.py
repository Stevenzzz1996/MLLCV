#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/28 17:36

def count_sort(s):
    # 找到最大最小值
    min_num = min(s)
    max_num = max(s)
    # 计数列表
    count_list = [0]*(max_num-min_num+1)
    # 计数
    for i in s:
        count_list[i-min_num] += 1
    s.clear()
    # 填回
    for ind,i in enumerate(count_list):
        while i != 0:
            s.append(ind+min_num)
            i -= 1

nums = [2,8,7,1,3,5,6,4]
count_sort(nums)
print(nums)