#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/28


# 滑动窗口的最大值
"""
n = int(input())
nums = list(map(int, input().split()))
ks = int(input())
res = []
res.append(max(nums[:ks]))
for i in range(1, n - ks + 1):
    if nums[i-1] == res[-1]:
        res.append(max(nums[i:i+ks]))
    else:
        res.append(max(res[-1], nums[i + ks - 1]))
res = [str(i) for i in res]
print(' '.join(res))
"""
def f(n,nums,ks):
    res = []
    res.append(max(nums[:ks]))
    for i in range(1, n - ks + 1):
        if nums[i-1] == res[-1]:
            res.append(max(nums[i:i+ks]))
        else:
            res.append(max(res[-1], nums[i + ks - 1]))
    res = [str(i) for i in res]
    print(' '.join(res))

n = int(input())
nums = list(map(int, input().split()))
ks = int(input())
f(n,nums,ks)