#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/28 17:36


def radix_sort(s):
    """基数排序"""
    i = 0  # 记录当前正在排拿一位，最低位为1
    max_num = max(s)  # 最大值
    j = len(str(max_num))  # 记录最大值的位数
    while i < j:
        bucket_list =[[] for _ in range(10)] #初始化桶数组
        for x in s:
            bucket_list[int(x / (10**i)) % 10].append(x) # 找到位置放入桶数组
        s.clear()
        for x in bucket_list:   # 放回原序列
            for y in x:
                s.append(y)
        i += 1

nums = [2,8,7,1,3,5,6,4]
radix_sort(nums)
print(nums)