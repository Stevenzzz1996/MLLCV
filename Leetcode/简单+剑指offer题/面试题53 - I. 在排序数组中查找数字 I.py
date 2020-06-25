#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 9:30


def search(nums, target):
    l, r = 0, len(nums)   # 假设len-1，则无法找到【1】， 一般是len-1，此处特殊需要扩大范围，
    while l < r:  # 此处不相等 ，如果等于会陷入死循环！比如没找到6时，会一直找！
        mid = (l+r) >> 1
        if target > nums[mid]:
            l = mid+1  # 这里也要考虑mid是否加1，一般帅是左边加1，过来一点
        elif target < nums[mid]:
            r = mid  # 这里也要考虑mid是否加1  ，一般是右边不减1，右边要是剪了，会越界！
        else:   # 从中间向左右扩大搜索，找完了直接返回！
            i = j = mid
            while i >= 0 and nums[i] == target:
                i -= 1
            while j <= len(nums)-1 and nums[j] == target:
                j += 1
            return j-i-1   # j多加了一次，i也多加了一次，所以是-2，本来是j-i+1的

    return 0

print(search(nums = [5,7,7,8,8,10], target = 6))
