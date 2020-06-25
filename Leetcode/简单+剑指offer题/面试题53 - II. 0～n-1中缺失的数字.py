#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 10:05


# 二分可以加快速度！
def misingNumber(nums):
    l, r = 0, len(nums)-1
    while l <= r:
        mid = (l+r) // 2
        if nums[mid] != mid:
            r = mid-1
        else:  # 等于就说明前面没空！
            l = mid+1

    return l   # 走到最后就行了！
print(misingNumber([0,1,2,3,5,6,7,8]))
