#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/29 20:30


def findMedianSortArrays(nums1, nums2):

    def findKthElements(arr1, arr2, k):
        len1, len2 = len(arr1), len(arr2)
        if len1 > len2:
            return findKthElements(arr2, arr1, k)  # 短的放左边
        if not arr1:
            return arr2[k-1]   # 终止条件，特判，作为索引要-1得到对应的值
        if k == 1:
            return min(arr2[0], arr1[0])
        i, j = min(k // 2, len1) - 1, min(k // 2, len2) - 1  # 索引用于比较
        if arr1[i] > arr2[j]:
            return findKthElements(arr1, arr2[j + 1:], k - j - 1)
            # j+1个数不考虑在中位数范围内，因为j是索引，所以是k -（j+1）
        else:
            return findKthElements(arr1[i + 1:], arr2, k - i - 1)

    l1, l2 = len(nums1), len(nums2)
    left = (l1 + l2 + 1) // 2
    right = (l1 + l2 + 2) // 2
    return (findKthElements(nums1, nums2, left) + findKthElements(nums1, nums2, right)) / 2

nums1 = [1, 2, 10]
nums2 = [3, 4, 5, 8]
print(findMedianSortArrays(nums2, nums1))
