#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 9:03


def reversePairs(nums):
    cnt = 0
    for i in range(len(nums)-1):   # 这里i不能到最后！
        for j in range(i+1, len(nums)):  # 这里不能到i！
            if nums[i] > nums[j]:
                cnt += 1

    return cnt