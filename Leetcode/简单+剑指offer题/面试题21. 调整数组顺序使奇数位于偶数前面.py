#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 11:00

from typing import List
def exchange(nums: List[int]) -> List[int]:
    i, j = 0, len(nums) - 1
    while i < j:
        if nums[i] % 2 == 0 and nums[j] % 2 == 1:
            nums[i], nums[j] = nums[j], nums[i]
            i += 1
            j -= 1
        elif nums[i] % 2 == 1 and nums[j] % 2 == 0:
            i += 1
            j -= 1
        elif nums[i] % 2 == 0 and nums[j] % 2 == 0:
            j -= 1
        else:
            i += 1
    return nums

nums = [1,2,3,4]
print(exchange(nums))


        '''
        res = []

        for num in nums:
            if num % 2 == 0:
                res.append(num)
            else:
                res.insert(0, num)
        return res
        '''