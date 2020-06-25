#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/26 17:47


def subsets2(nums):
    nums.sort()
    res = []

    def helper(i, tmp):
        res.append(tmp)
        for j in range(i, len(nums)):
            if j > i and nums[j] == nums[j - 1]:
                continue
            else:
                helper(j + 1, tmp + [nums[j]])

    helper(0, [])
    return res

nums = [1,2,2]
print(subsets2(nums))