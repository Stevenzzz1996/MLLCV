#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/26 16:47


class Solution:
    def subsets(nums):
        res = []
        n = len(nums)
        def helper(i, tmp):
            res.append(tmp)
            for j in range(i, n):
                helper(j+1, tmp+[nums[j]])

        helper(0, [])
        return res

nums = [1,2,3]
print(Solution.subsets(nums))
