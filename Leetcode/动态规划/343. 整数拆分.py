
#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/24 21:42


class Solution:
    def integerBreak(self, n: int) -> int:
        dp = [1] * (n + 1)
        for i in range(2, n + 1):
            for j in range(1, i):
                dp[i] = max(dp[i], max(j, dp[j]) * max(i - j, dp[i - j]))  # 不切，从j处切（i，j*（i-j））
                # 因为每个数都要拆成两个，但是像数字2最大乘积却为1
        return dp[-1]

'''
if n <= 3: return n - 1
a, b = divmod(n, 3)
if b == 0: return 3 ** a
if b == 1: return 3 ** (a - 1) * 4
return 3 ** a * 2
'''