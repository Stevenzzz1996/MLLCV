#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/26 11:33


"""
sum(P) - sum(N) = target（两边同时加上sum(P)+sum(N)）
sum(P) + sum(N) + sum(P) - sum(N) = target + sum(P) + sum(N)
 (因为 sum(P) + sum(N) = sum(nums))
 2 * sum(P) = target + sum(nums)
因此，原来的问题已转化为一个求子集的和问题： 找到nums的一个子集 P，使得 P = (sum(nums)+target)//2

开辟一个长度为P+1的数组，命名为dp
dp的第x项，代表组合成数字x有多少方法。比如说,dp[0] = 1，代表组合成0只有1中方法，即什么也不取。比如说dp[5] = 3 ，
代表使总和加到5总共有三种方法。所以最后返回的就是dp[P]，not 代表组合成P的方法有多少种

怎么更新dp数组呢？

遍历nums，遍历的数记作num
再逆序遍历从P到num，遍历的数记作j
更新dp[j] = dp[j - num] + dp[j]

"""
# 难点在于将问题转为 P = (sum(nums)+target)//2
class Solution:
    def targetSum(self, nums, target):
        if sum(nums) < target or (sum(nums)+target) % 2 != 0: return 0
        P = (sum(nums)+target)//2
        dp = [1]+[0]*P
        for num in nums:
            for j in range(P, num-1, -1):
                dp[j] += dp[j-num]
        return dp[-1]

# class Solution:
#     def findTargetSumWays(self, nums: List[int], target: int) -> int:
#         if sum(nums) < target or (sum(nums)+target) % 2 != 0: return 0
#         P = (sum(nums)+target)//2
#         dp = [1] + [0] * P
#         for i in range(len(nums)):
#             for j in range(P,nums[i]-1,-1):
#                 dp[j] += dp[j-nums[i]]
#         return dp[-1]
# 同组合总和4

if __name__ == '__main__':
    print(Solution().targetSum([1, 1, 1, 1, 1],3))