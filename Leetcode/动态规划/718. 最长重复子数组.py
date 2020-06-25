#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/5 14:57


class Solution:
    def findLength(self, A: List[int], B: List[int]) -> int:
        dp = [[0]*(len(B)+1) for _ in range(len(A)+1)]
        res = 0
        for i in range(len(A)):
            for j in range(len(B)):
                if A[i] == B[j]:
                    dp[i+1][j+1] = dp[i][j]+1
                    res = max(dp[i+1][j+1], res)
        return res