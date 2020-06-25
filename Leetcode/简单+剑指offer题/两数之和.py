#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/29 17:55


#用一个for循环
def twoSum(nums,target):
    j = -1
    for i in range(len(nums)):
        tmp = nums[:i]
        nums2 = target - nums[i]
        if nums2 in tmp:
            j = tmp.index(nums2)
            break
    if j >= 0:
        return [i, j]

nums = [2, 7, 11, 15]
target = 13
print(twoSum(nums,target))
'''
for i in range(n):
    tmp = target - nums[i]
    if tmp in nums: # 判断a有没有在nums数组里
        j = nums.index(tmp) # 有的话，那么用index获取到该数字的下标
        if i == j: 
            continue # 同样的数字不能重复用，所以这里如果是一样的数字，那么就不满足条件，跳过
        else: # 否则就返回结果
            return i,j
            break
    else: 
        continue # 上面的条件都不满足就跳过，进行下一次循环
'''