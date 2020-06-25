#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 21:46

class Solution:
    def isStraight(nums):
        nums.sort()
        ghost = 0
        for i in range(len(nums)-1):
            if nums[i] == 0:  # 王的数量
                ghost += 1
            else:
                if nums[i] == nums[i+1]:  # 如果有相等的直接错！
                    return False
                ghost -= nums[i+1]-nums[i]-1  # 比如5-4=1，就不要王！
                if ghost < 0:
                    return False
        return True
if __name__ == '__main__':
    print(Solution.isStraight([1,2,3,4,9]))

