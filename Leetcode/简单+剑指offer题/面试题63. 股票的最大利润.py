#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 21:46


# 找前面的最小值，找后面的最大值！
def maxProfit(prices):
    min_p, max_p = float("inf"), 0
    for i in range(len(prices)):
        min_p = min(min_p, prices[i])
        max_p = max(max_p, prices[i]-min_p)
    return max_p
print(maxProfit([7,1,5,3,6,4]))