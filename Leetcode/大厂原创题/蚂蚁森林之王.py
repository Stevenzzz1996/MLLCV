#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/13 19:40


# int(input())
# list1 = []
# list1.append(input().split())
n = 4
list1 = [0,1,1,1]
dp = [1 for _ in range(n)]

for i in range(n):
    for j in (i+1, n):
        if list1[j] == i+1:
            dp[i] += 1

print(dp)
