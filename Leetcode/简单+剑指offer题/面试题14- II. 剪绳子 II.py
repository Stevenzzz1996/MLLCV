#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 9:31


def cuttingRope( n: int) -> int:
    dp = [1]*(n+1)
    for i in range(3, n+1):
        for j in range(1,i):
            dp[i] = max(dp[i], max((i-j)*j, j * dp[i-j]))
    return dp[-1] % 1000000007

print(cuttingRope(10))