#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/29 17:18


def canPartitionKSubsets(nums, k):
    _sum_ = sum(nums)
    goal = _sum_ // k
    nums.sort(reverse=True)
    if _sum_ % k or nums[0] > goal:
        return False  # 余数不为0,最大值大于goal
    def dfs(nums, total):
        if total == goal:
            if not nums:
                return True
            return dfs(nums, 0)
        for i, j in enumerate(nums):
            if total+j <= goal and dfs(nums[:i]+nums[i+1:], total+j):
                return True
        return False

    return dfs(nums, 0)

nums = [4, 3, 2, 3, 5, 2, 1]
k = 4

print(canPartitionKSubsets(nums,k))