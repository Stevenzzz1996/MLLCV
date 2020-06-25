#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 10:12


def myPow(x,n):
    if n == 0: return 1
    if n == 1: return x
    if n < 0:
        n = -n
        x = 1/x
    res = 1
    while n:
        if n & 1:   #是奇数得话或者 认为是右边为1的话（二进制）不为1就是0就不操作！
            res *= x
        x *= x
        n >>= 1
    return res
print("%.5f" % myPow(2.00000, 10))