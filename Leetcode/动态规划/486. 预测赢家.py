#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/6 10:47


# 核心思想就是动态规划，用一个二维数据dp记录当前情况是从i到j时，先取分数的人，能比后取分数的人多得多少分。
#
# length=j-i+1从1开始递增：
# 1、当长度是1时，先取数的可以多得nums[i]分；
# 2、当长度是2时，先取数的人取两个数中较大的数，最终比后取数的人多得abs(nums[i] - nums[j])；
# 3、当长度大于等于3时，可能先取左边的数，也可能先取右边的数，
# 分别可以多得nums[i] - dp[i + 1][j]和num[j] - d[i][j - 1]分，取两者中较大的数即可。

class Solution:
    def PredictTheWinner(self, nums) -> bool:
        n = len(nums)
        if n == 1: return True
        dp=[[0]*n for _ in range(n)]
        for length in range(1, n+1):
            for i in range(n-length+1):
                j = i+length-1  # i是第一个，j是最右边一个，length是长度！难点所在
                if length == 1:
                    dp[i][j] = nums[i]
                elif length == 2:
                    dp[i][j]=nums[i]-nums[j] if nums[i]>=nums[j] else nums[j]-nums[i]
                else:  # 其它情况！
                    dp[i][j] = max(nums[i]-dp[i+1][j],nums[j]-dp[i][j-1])

        return True if dp[0][-1] >= 0 else False

if __name__ == '__main__':
    print(Solution().PredictTheWinner([1, 5, 233, 7]))


# class Solution:
#     def stoneGame(self, piles) -> bool:
#         n = len(piles)
#         dp = [[0] * n for _ in range(n)]  # 能多拿的石子数
#
#         for i in range(n):  # 始化只有i一个石头堆的情形，初始化只需要考虑有一个石头堆的情况，很简单：
#             dp[i][i] = piles[i]
#
#         for i in range(n - 1):
#             for j in range(n):
#                 dp[i][j] = max(piles[i] - dp[i + 1][j], piles[j] - dp[i][j - 1])
#
#         return dp[0][n - 1] > 0
#
#
# if __name__ == '__main__':
#     print(Solution().stoneGame([1, 5, 233, 7]))
