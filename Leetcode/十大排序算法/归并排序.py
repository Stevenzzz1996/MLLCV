#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/28 17:35


# 原理：基本思路是不断将两个有序的序列合并为一个大的有序序列。
# 具体操作时，首先将序列分为两部分，然后对每一部分进行循环递归，再逐个将结果进行归并。归并排序是一种 稳定排序 。
# 快速排序包括一个选择操作过程（确定a[r]的正确位置），后跟两个递归调用。
# 归并排序的执行过程和快速排序相反，两个递归调用之后是一个归并过程。
#
# 代码实现：
# 时间复杂度：“快些以nlogn的速度归队”（快：快速排序，些：希尔排序，归：归并排序，队：堆排序）
# 空间复杂度：快速排序为O(nlogn)，这几个里面其他的都是O(1)
# 稳定性：“心情不稳定，快些选一堆好友聊天”（快：快速排序，些：希尔排序，选：直接选择排序，堆：堆排序）
def merge_sort(arr):  # 两两拆分
    if len(arr) == 1: return arr  # 剩余一个元素时结束，即完成将所有元素划分开了。
    mid = len(arr) - 1
    left = arr[:mid]
    right = arr[mid:]
    return marge(merge_sort(left), merge_sort(right))

def marge(left,right):  #两两比较合并
    res = []
    while len(left) > 0 and len(right) > 0:
        # 左右两个数列第一个最小放前面
        if left[0] > right[0]:
            res.append(right.pop(0))
        else:
            res.append(left.pop(0))

    res += left
    res += right
    return res

nums = [2, 8, 7, 1, 3, 5, 6, 4]
print(merge_sort(nums))
