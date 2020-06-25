#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/6 21:36

#解决LIS类问题，最直接的灵感是DP。dp[i]表示在i个元素时，其LIS的长度。算法复杂度为O(n^2)但是DP解法是有优化空间：
class Solution(object):
    def lengthOfLIS(self, nums):
        if not nums:
            return 0
        dp = [0] * len(nums)
        res = 1
        for i in range(len(nums)):
            tmp = 1
            for j in range(i):
                if nums[i] > nums[j]:
                    tmp = max(tmp, dp[j] + 1)
            dp[i] = tmp
            res = max(res, dp[i])
        return res
# 贪心+二分优化！
class Solution(object):
    def bestSeqAtIndex(self, height, weight):
        if not height: return 0
        length = len(height)
        actors = [(height[i], weight[i]) for i in range(length)]
        actors.sort(key=lambda x:(x[0], -x[1]))
        tail = [0] * length
        size = 0
        for actor in actors:
            i, j = 0, size
            while (i != j):
                mid = (i + j) // 2
                if tail[mid] < actor[1]: i = mid + 1
                else: j = mid
            tail[i] = actor[1]
            if i == size: size += 1
        return size
if __name__ == '__main__':
    print(Solution().bestSeqAtIndex(height = [65,70,56,75,60,68],weight = [100,150,90,190,95,110]))