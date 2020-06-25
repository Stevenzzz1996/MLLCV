#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/28 17:35



def bucket_sort(s):
    min_num = min(s)
    max_num = max(s)
    # 桶的大小
    bucket_range = (max_num - min_num) / len(s)
    # 桶数组
    count_list = [[] for i in range(len(s) + 1)]
    # 向桶数组填数
    for i in s:
        count_list[int((i - min_num) // bucket_range)].append(i)
    s.clear()
    # 回填，这里桶内部排序直接调用了sorted
    for i in count_list:
        for j in sorted(i):
            s.append(j)

nums = [2,8,7,1,3,5,6,4]
bucket_sort(nums)
print(nums)
