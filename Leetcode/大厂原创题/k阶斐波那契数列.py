#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/12 17:08

k = input()
n = input()

def fib(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    # if n<k-1: return 0
    # if n==k-1: return 1
    # res=0
    # for i in range(n-k,n):
    #     i+=1
    dp = [0 for _ in range(n+1)]
    dp[1] = 1
    for i in range(2, n+1):
            dp[i] = 2*dp[i-1] - dp[i-k-1]

    return dp[-1] % 397
print(fib(n))
#未动