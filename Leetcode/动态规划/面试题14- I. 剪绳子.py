#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/5 15:41


# 给你一根长度为 n 的绳子，请把绳子剪成整数长度的 m 段（m、n都是整数，n>1并且m>1），
# 每段绳子的长度记为 k[0],k[1]...k[m-1] 。请问 k[0]*k[1]*...*k[m-1] 可能的最大乘积是多少？
# 例如，当绳子的长度是8时，我们把它剪成长度分别为2、3、3的三段，此时得到的最大乘积是18。
#

# 边界条件：dp[1] = dp[2] = 1, 表示长度为 2 的绳子最大乘积为 1

# 状态转移方程：dp[i] = max(dp[i], max((i - j) * j, j * dp[i - j]))，可以这样理解：

class Solution:
    def cuttingRope(self, n: int) -> int:
        dp = [0 for _ in range(n + 1)]  # dp[0] dp[1]其实没用
        dp[2] = 1  # 初始化
        for i in range(3, n + 1):   # i代表长度！
            for j in range(i):
                dp[i] = max(dp[i], max((i - j) * j, j * dp[i - j]))
        return dp[n] % 1000000007  # 取模
