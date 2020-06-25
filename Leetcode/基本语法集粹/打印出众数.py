#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/6/3 20:43


arr_appear = dict((a, arr.count(a)) for a in arr);
#
# 1. 遍历一个数组,输出其重复元素。
# 示例1：
# 输入: 数组[1,1,1,2,9,10]
#
# def duplicateElementCheckForArray(array):
#
# lookup={}
# for i in range(len(array)):
# if array[i] not in lookup:
# lookup[i]=1
# else:
# lookup[i]+=1
# return lookup
def majorityElement(self, nums):
    """
    :type nums: List[int]
    :rtype: int
    """
    if len(nums) == 1:
        return nums[0]
    numDic = {}
    for i in nums:
        if numDic.has_key(i):
            numDic[i] += 1
            if numDic.get(i) >= (len(nums) + 1) / 2:
                return i
        else:
            numDic[i] = 1

def majorityElement1(self, nums):
    """
    :type nums: List[int]
    :rtype: int
    """
    for i in nums[len(nums) // 2:]:
        if nums.count(i) > len(nums) // 2:
            return i
