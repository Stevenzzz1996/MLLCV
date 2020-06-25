#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/29 19:41


def wiggleMaxLength(nums):
    if len(nums)<2:
        return len(nums)
    # flip是状态，表示前一个数字是处在峰还是谷，res是最终的结果，k是迭代的时候的下标
    flip = -1
    k = 1
    res = 1
    while k < len(nums):
        if nums[k] == nums[k-1]:
            k += 1
            continue  # 重复的值直接跳过
        f = 1 if nums[k] > nums[k-1] else 0  # 把大值变为1，小值标为0！
        if f != flip:  # 说明与前一个值不同！
            res += 1
            flip = f  # 定位到前一个值，紧跟着！
        k += 1
    return res if res > 0 else 1
# 其实我们只关心数组中的上下抖动就好了，不需要关心数字是几
# 例如：
# [1, 1, 1, 17,5,10,13,15,10,5,16,8] 就是数组
# [-1,-1,-1,1, 0,1, 1, 1, 0, 0,1, 0]
# 1代表比前一个大
# 0代表比前一个小
# -1是开始的标志
# 我们设置flip初始值为-1，ans为1
# 原来的数组 ： [1, 1, 1, 17,5,10,13,15,10,5,16,8]
# flip ： [-1,-1,-1,1, 0,1, 1, 1, 0, 0,1, 0]
# res ： [1, 1, 1, 2, 3,4, 4, 4, 5, 5,6, 7]



nums=[1,17,5,10,13,15,10,5,16,8]
if __name__ == '__main__':
    print(wiggleMaxLength(nums))

# def wiggleMaxLength(nums):
#     if not nums:
#         return 0
#     res = []
#     dp = [[1 for i in range(2)] for j in range(len(nums))]
#     res.append(dp[0][0])
#     res.append(dp[0][1])
#     for i in range(1,len(nums)):
#         for j in range(i):
#             if nums[i] > nums[j]:
#                 dp[i][1] = max(dp[i][1],dp[j][0]+1)
#             elif nums[i] < nums[j]:
#                 dp[i][0] = max(dp[i][0],dp[j][1]+1)
#             else:               #若nums[i]=nums[j]，此时nums[i]不可能加在nums[j]后面
#                 continue
#         res.append(dp[i][0])
#         res.append(dp[i][1])
#     return max(res)
# nums=[1,17,5,10,13,15,10,5,16,8]
# print(wiggleMaxLength(nums))