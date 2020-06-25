#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/28


# 步骤1:比较相邻的元素。如果第一个比第二个大，就交换它们两个；
# 步骤2:对每一对相邻元素作同样的工作，从开始第一对到结尾的最后一对，这样在最后的元素应该会是最大的数；
# 步骤3:针对所有的元素重复以上的步骤，除了最后一个；
# 步骤4:重复步骤1~3，直到排序完成。
# 因为这个排序的过程很像冒泡泡，找到最大的元素不停的移动到最后端，所以这个排序算法就叫冒泡排序。
# 优化的冒泡
# 12345987 其中12345已经排好序列，这样会避免不必要的时间浪费。

def bubble_sort(nums):
    for i in range(len(nums)-1):
        flag = False
        for j in range(len(nums)-i-1):
            if nums[j] > nums[j+1]:
                nums[j], nums[j+1] = nums[j+1], nums[j]
                flag = True
        if not flag:
            return nums


nums = [1,2,3,4,7,5,6]
print(bubble_sort(nums))