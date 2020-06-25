#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/1 16:59、


# 相当于排序算法，每轮吧最小的拍到最前面！
def minNumber(nums) -> str:
    if not nums: return ""
    for i in range(len(nums)):
        nums[i] = str(nums[i])
    for i in range(len(nums)):
        for j in range(i+1, len(nums)-1):   # 经过内部第一轮之后，第一个已经是最小的字符串了！每轮下来i为最小的！
            if int(nums[i]+nums[j]) > int(nums[j]+nums[i]):
                nums[i], nums[j] = nums[j], nums[i]
    return "".join(nums)

print(minNumber([3,30,34,5,9]))

