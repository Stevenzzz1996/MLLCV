#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/26 17:46


def permute(nums):
    res = []
    def helper(nums, tmp):
        if not nums:
            res.append(tmp)
        for i in range(len(nums)):
            helper(nums[:i]+nums[i+1:], tmp + [nums[i]])

    helper(nums, [])
    return res

nums = [1,2,3]
print(permute(nums))