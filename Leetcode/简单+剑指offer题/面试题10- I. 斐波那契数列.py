#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/30 15:49


# def fib(n):
#     if n == 0:
#         return 0
#     if n == 1:
#         return 1
#     return (fib(n - 1) + fib(n - 2)) % 1000000007
# def fib(n):
#   if n == 0:
#         return 0
#         if n == 1:
#             return 1
#         dp = [0 for _ in range(n+1)]
#         dp[1] = 1
#         for i in range(2, n+1):
#             dp[i] = dp[i-1] + dp[i-2]
#         return dp[n] % 1000000007
#         '''



def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a % 1000000007
print(fib(2))