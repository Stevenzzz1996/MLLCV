#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/29 22:03

class Solution:
    def climbStairs(self, n):
        dp = [0]*(n+1)
        dp[1] = 1
        dp[2] = 2
        if n <= 2: return dp[n]
        for i in range(3, n+1):
            dp[i] = dp[i-1]+dp[i-2]
        return dp[-1]

if __name__ == '__main__':
    print(Solution().climbStairs(3))