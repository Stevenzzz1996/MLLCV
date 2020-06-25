#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 19:24


def maxSlidingWindow(nums,k):
    res = [max(nums[:k])]  # 先取出第一个窗口的最大值，便于后面判断
    for i in range(1, len(nums)-k+1):
        if nums[i-1] != res[-1]:   # 如果最大值是第一个，后面的需要重新比
            res.append(max(nums[i+k-1], res[-1]))
        else:  # 如果在后面得话，前面窗口最大值就是上一个！节省时间！
            res.append(max(nums[i:i+k]))
    return res

# 这道题其实是想考队列！
# 一个双端的队列只用来存储最大的元素的下标
#         deque, res, n = [], [], len(nums)
#         for i in range(n):
#             while deque and deque[0] < i-k+1:
#                 deque.pop(0)
#             while deque and nums[i] > nums[deque[-1]]:
#                 deque.pop(-1)
#             deque.append(i)
#             if i >= k-1:
#                 res.append(nums[deque[0]])
#         return res

print(maxSlidingWindow(nums=[1,3,-1,-3,5,3,6,7], k = 3))


