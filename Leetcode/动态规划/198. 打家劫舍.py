#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/5 16:08


# 如果两间相邻的房屋在同一晚上被小偷闯入，系统会自动报警。
# 链表 空间优化！
from typing import List


class Solution:
    def rob(self, nums: List[int]) -> int:
        cur, pre = 0, 0
        for num in nums:
            cur, pre = max(pre + num, cur), cur
        return cur


if __name__ == '__main__':
    print(Solution().rob([1,2,3,1]))

# def rob(self, nums: List[int]) -> int:
#     if len(nums) == 0: return 0
# 子问题：f(k) = 偷 [0..k) 房间中的最大金额
#     N = len(nums)
#     dp = [0] * (N+1)
#     dp[0] = 0
#     dp[1] = nums[0]
#     for k in range(2, N+1):
#         dp[k] = max(dp[k-1], nums[k-1] + dp[k-2])
#     return dp[N]


# 围成一圈！
class Solution:
    def rob(self, nums: List[int]) -> int:
        def my_rob(nums):
            cur, pre = 0, 0
            for num in nums:
                cur, pre = max(pre + num, cur), cur
            return cur
        return max(my_rob(nums[:-1]),my_rob(nums[1:])) if len(nums) != 1 else nums[0]