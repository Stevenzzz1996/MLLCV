#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/3 21:45


# 给你一个整数数组nums，请你找出数组中乘积最大的连续子数组（该子数组中至少包含一个数字），并返回该子数组所对应的乘积。
class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        n = len(nums)
        max_res = -float("inf")
        max_num = 1
        min_num = 1
        for i in range(n):
            if nums[i] < 0:  # 当前
                max_num, min_num = min_num, max_num
            max_num = max(max_num*nums[i], nums[i])
            min_num = min(min_num*nums[i], nums[i])
            max_res = max(max_num, max_res)
        return max_res