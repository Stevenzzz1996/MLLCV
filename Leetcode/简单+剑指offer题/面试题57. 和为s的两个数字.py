#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 16:30


def twoSum(nums,target):
    if nums[0] > target: return
    l,r = 0, len(nums)-1
    while l < r: # 取两个数千万不能等啊
        mid = (l + r) // 2
        if target < nums[mid]:
            r = mid-1   # 都小于了，直接到左边一位！
        else:
            while l < r:
                if nums[l]+nums[r] < target:
                    l += 1
                elif nums[l]+nums[r] > target:
                    r -= 1
                else:
                    return [nums[l], nums[r]]   #直接在这里返回！

print(twoSum(nums = [2,7,11,15], target = 9))
