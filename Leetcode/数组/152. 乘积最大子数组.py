#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/4 18:08

class Solution:
    def maxProduct(self,nums):
        n=len(nums)
        max_res = -float("inf")
        max_num = 1
        min_num = 1
        for i in range(n):
            if nums[i] < 0:
                max_num,min_num = min_num, max_num
            max_num = max(max_num * nums[i], nums[i])
            min_num = min(min_num*nums[i], nums[i])
            max_res =max(max_num, max_res)  # 实时存取最大值，如果遇到更大，继续更新！

        return max_res

if __name__ == '__main__':
    print(Solution().maxProduct([2,3,-5,4]))
