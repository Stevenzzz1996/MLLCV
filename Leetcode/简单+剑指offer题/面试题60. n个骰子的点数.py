#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 19:53


class Solution:
    def twoSum(self, n: int) -> List[float]:
        dp = [[0 for i in range(6 * n)] for i in range(n)]

        for i in range(6):
            dp[0][i] = 1
        for i in range(1, n):  # 1，相当于2个骰子。
            for j in range(i, 6 * (i + 1)):  # [0,i-1]的时候，频数为0（例如2个骰子不可能投出点数和为1）
                dp[i][j] = dp[i - 1][j - 6] + dp[i - 1][j - 5] + dp[i - 1][j - 4] + \
                           dp[i - 1][j - 3] + dp[i - 1][j - 2] + dp[i - 1][j - 1]

        count = dp[n - 1]
        return count  # 算得骰子投出每一个点数的频数。再除以总的排列数即可得到频率
