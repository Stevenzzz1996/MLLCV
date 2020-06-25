#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/28


# 最小的排在最前面，第一轮就不动这个最左边的最小值。。。
# 选择最小值
def selection_sort(nums):
    for i in range(len(nums)):
        min_idx = i
        for j in range(i+1, len(nums)):
            if nums[min_idx] > nums[j]:
                min_idx = j

        nums[min_idx], nums[i] = nums[i], nums[min_idx]

    return nums

nums = [1,2,3,4,7,5,6]
print(selection_sort(nums))
