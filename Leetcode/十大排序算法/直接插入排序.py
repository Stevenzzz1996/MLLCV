#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/28 15:55


# 插入排序的核心思想是遍历整个数组，保持当前元素左侧始终是排序后的数组，
# 然后将当前元素插入到前面排序完成的数组的对应的位置，使其保持排序状态。
# 有点动态规划的感觉，类似于先把前i-1个元素排序完成，再插入第i个元素，构成i个元素的有序数组。

# 从第二个元素开始和前面的元素进行比较，
# 如果前面的元素比当前元素大，则将前面元素 后移，当前元素依次往前，
# 直到找到比它小或等于它的元素插入在其后面。

def insert_sort(nums):
    # 第一层for循环代表要插入的次数
    for i in range(len(nums)):
        for j in range(i, 0, -1):
            if nums[j] < nums[j-1]:
                nums[j], nums[j-1] = nums[j-1], nums[j]
            else:
                break

    return nums

nums = [1,2,3,4,7,5,6]
print(insert_sort(nums))
