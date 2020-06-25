#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/30 13:49


class Solution:
    def insert(intervals, newInterval):
        #三中特殊情况：
        if not intervals: return [newInterval]
        if newInterval[1] < intervals[0][0]: return [newInterval] + intervals
        if newInterval[0] > intervals[-1][1]: return intervals + [newInterval]
        i = 0
        n = len(intervals)
        while i < n and newInterval[0] > intervals[i][1]:  # 首先找到新区间的位置
            i += 1
        left = min(intervals[i][0], newInterval[0])
        tmp = i
        if intervals[i][0] > newInterval[1]:
            return intervals[:tmp] + [newInterval] + intervals[tmp:]
        right = newInterval[1]
        while i < n and newInterval[1] >= intervals[i][0]:
            right = max(right, intervals[i][1])
            i += 1
        return intervals[:tmp] + [[left, right]] + intervals[i:]

if __name__ == '__main__':
    print(Solution.insert(intervals = [[1,3],[6,9]], newInterval = [4,7]))