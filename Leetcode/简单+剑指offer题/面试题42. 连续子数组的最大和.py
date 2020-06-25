#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/1 12:55


def maxSubArray(nums) -> int:
    if not nums: return 0
    for i in range(1, len(nums)):
        nums[i] += max(nums[i - 1], 0)
    return max(nums)  # 直接操作原数组，最大的即为所求

    # max_num = nums[0]
    # for i in range(1, len(nums)):
    #     if nums[i - 1] > 0:
    #         nums[i] += nums[i - 1]
    #     max_num = max(max_num, nums[i])
    # return max_num

print(maxSubArray(nums = [-2,1,-3,4,-1,2,1,-5,4]))