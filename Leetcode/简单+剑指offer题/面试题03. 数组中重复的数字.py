#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/30 11:19



#def findRepeatNumber(self, nums):
#     dic = {}
#     for i in nums:
#         if i not in dic:
#             dic[i] = 0
#         else:
#             return i
#

#下标索引法
#把索引对应的数字填过去

def findRepeatNumber(nums):
    for i in range(len(nums)):
        while nums[i] != i:
            if nums[i]== nums[nums[i]]:
                return nums[i]
            nums[nums[i]], nums[i] = nums[i], nums[nums[i]]

nums=[2, 3, 1, 0, 2, 5, 3]
print(findRepeatNumber(nums))


