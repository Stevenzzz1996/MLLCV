#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/24 21:06


# 给定一个非负整数 num。对于 0 ≤ i ≤ num 范围中的每个数字 i ，
# 计算其二进制数中的 1 的数目并将它们作为数组返回。
class Solution:
    def countBits(self, num: int) -> List[int]:
        dp = [0]*(num+1)
        for i in range(1, num+1):
            if i % 2 != 1:
                dp[i] = dp[i//2]
            else:
                dp[i] = dp[i-1]+1
        return dp


'''
        dp = [0]
        for i in range(1, num + 1):
            dp.append(dp[i>>1] + (i&1))
        return dp
         dp问题: dp[i] = dp[i>>1] + (i&1).
            i>>1代表前一个二进制位的次数,
            i&1代表i的末尾是否为1
'''
