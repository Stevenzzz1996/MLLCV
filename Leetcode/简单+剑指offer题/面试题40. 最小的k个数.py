#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/1 11:03


# 快排 或最小堆python默认最小堆
class Solution:
    def getLeastNumbers(self, nums: List[int], k: int) -> List[int]:
        if k == 0: return []
        n, opposite = len(nums), [-1 * x for x in nums[:k]]
        heapq.heapify(opposite)
        for i in range(k, len(nums)):
            if -opposite[0] > nums[i]:
                # 维持堆大小不变
                heapq.heappop(opposite)
                heapq.heappush(opposite, -nums[i])
        return [-x for x in opposite]


