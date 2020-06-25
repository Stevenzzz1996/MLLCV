#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/27 21:26




# dp[i][k]表示到数组第i为底公差为k的超过长度3的个数
# 直接转移方程
# dp[i][k] += 1 + dp[j][k], j < i

class Solution:
    def numberOfArithmeticSlices( A):
        from collections import defaultdict
        dp = [defaultdict(int) for _ in range(len(A))]
        res = 0
        for i in range(len(A)):
            for j in range(i):
                k = A[i] - A[j]
                dp[i][k] += dp[j][k] + 1
                # 说明满足长度大于等于3
                if k in dp[j]:
                    res += dp[j][k]
        return res

if __name__ == '__main__':
    print(Solution.numberOfArithmeticSlices([2, 4, 6, 8, 10]))
