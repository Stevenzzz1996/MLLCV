#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/30 21:36


def cuttingRope(n):
    # if n <= 3: return n-1
    # div, mod =  divmod(n, 3)
    # if mod = 0: return math.pow(3,div)
    # elif mod = 1: return math.pow(3,div-1)*4
    # return math.pow(3,div)*2

    # 边界条件：dp[1] = dp[2] = 1，表示长度为 2 的绳子最大乘积为 1；
    # （dp[i]不再分了，）（继续在j处分一下不在分，）（j处取下来，i-j再继续分下去。）
    # 状态转移方程：dp[i] = max(dp[i], max((i - j) * j, j * dp[i - j]))

    dp = [0 for _ in range(n+1)]
    dp[2] = 1
    for i in range(3, n + 1):
        for j in range(1, i):
            dp[i] = max(dp[i], max(j * (i-j), j * dp[i-j]))
    return dp[-1]

print(cuttingRope(10))
