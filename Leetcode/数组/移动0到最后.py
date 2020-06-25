#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/22 8:32


from typing import List
class Solution:
    def moveZeroes(nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        if not nums: return 0
        j=0
        for i in range(len(nums)):
            if nums[i]:
                nums[i], nums[j] = nums[j], nums[i]
                j += 1

if __name__ == '__main__':
    nums = [0, 1, 0, 3, 12]
    Solution.moveZeroes(nums)
    print(nums)

