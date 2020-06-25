#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/23 10:48


# 几乎所有的动态规划解决方案，首先会创建一个一维或多维数组 DP 来保存中间子解的值，以及通常数组最后一个值代表最终解。注意，我们创建了一个虚构的元素 dp[0]=0 来简化逻辑，这有助于在在余数 (n-k）恰好是一个完全平方数的情况下。
# 我们还需要预计算小于给定数字 n 的完全平方数列表（即 square_nums）。
# 在主要步骤中，我们从数字 1 循环到 n，计算每个数字 i 的解（即 numSquares(i)）。每次迭代中，我们将 numSquares(i) 的结果保存在 dp[i] 中。
# 在循环结束时，我们返回数组中的最后一个元素作为解决方案的结果。
# 在下图中，我们演示了如何计算与 dp[4] 和 dp[5] 相对应的 numSquares(4) 和 numSquares(5) 的结果。

import math
class Solution(object):
    def numSquares(n):
        """
        :type n: int
        :rtype: int
        """
        square_nums = [i ** 2 for i in range(0, int(math.sqrt(n)) + 1)]

        dp = [float('inf')] * (n + 1)
        # bottom case
        dp[0] = 0

        for i in range(1, n + 1):
            for square in square_nums:
                if i < square:
                    break
                dp[i] = min(dp[i], dp[i - square] + 1)

        return dp[-1]

if __name__ == '__main__':
    n = 13
    print(Solution.numSquares(n))


# class Solution:
#     def numSquares(self, n: int) -> int:
#         dp=[i for i in range(n+1)]
#         for i in range(2,n+1):
#             for j in range(1,int(i**(0.5))+1):
#                 dp[i]=min(dp[i],dp[i-j*j]+1)
#         return dp[-1]