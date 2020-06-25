#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/23 17:32

# 除了缓存递归结果，我们还可以直接用自底向上的方式来填充 dp 数组。

# class Solution:
#     def maxCoins(self, nums: List[int]) -> int:
#
#         # reframe problem as before
#         nums = [1] + nums + [1]
#         n = len(nums)
#
#         # dp will store the results of our calls
#         dp = [[0] * n for _ in range(n)]
#
#         # iterate over dp and incrementally build up to dp[0][n-1]
#         for left in range(n-2, -1, -1):
#             for right in range(left+2, n):
#                 # same formula to get the best score from (left, right) as before
#                 dp[left][right] = max(nums[left] * nums[i] * nums[right] + dp[left][i] + dp[i][right] for i in range(left+1, right))
#
#         return dp[0][n-1]

from functools import lru_cache

class Solution:
    def maxCoins(self, nums: List[int]) -> int:

        # reframe the problem
        nums = [1] + nums + [1]

        # cache this
        @lru_cache(None)
        def dp(left, right):

            # no more balloons can be added
            if left + 1 == right: return 0

            # add each balloon on the interval and return the maximum score
            return max(nums[left] * nums[i] * nums[right] + dp(left, i) + dp(i, right) for i in range(left+1, right))

        # find the maximum number of coins obtained from adding all balloons from (0, len(nums) - 1)
        return dp(0, len(nums)-1)


