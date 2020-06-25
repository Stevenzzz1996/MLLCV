#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/30 16:04


def numWays(n):
    # 特判
    if n < 2: return 1
    dp = [1 for _ in range(n+1)]

    for i in range(2, n+1):
        dp[i] = dp[i-1] + dp[i-2]

    return dp[-1] % 1000000007
print(numWays(2))