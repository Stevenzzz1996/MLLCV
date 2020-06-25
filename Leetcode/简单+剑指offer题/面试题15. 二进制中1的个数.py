#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 9:48
# n >>= 1 ： 将二进制数字 nn 无符号右移一位（ Java 中无符号右移为 ">>>" ） 。

def hammingWeight(n):
    cnt=0
    while n:
        cnt += n & 1
        n >>= 1  # n//=2
    return cnt
n = 11
print(hammingWeight(n))
