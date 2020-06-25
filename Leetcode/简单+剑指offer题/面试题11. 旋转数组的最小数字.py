#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/30 16:14


def minArray(arr):
    l, r = 0, len(arr)-1

    while l < r:
        mid = (l + r) // 2
        if arr[mid] > arr[r]:
            # 说明最小的一定在右边，旋转的少3，4，5，1，2
            l = mid+1
        elif arr[mid]< r:
            # mid有可能是最小值，移动的多,或者全旋转了变为原来的5，1，2，3，4
            r = mid
        else:  # 有可能元素相等，2，2，2，0，2
            r -= 1
    return arr[r]  # l也可以

arr = [3, 4, 5, 1, 2]
print(minArray(arr))