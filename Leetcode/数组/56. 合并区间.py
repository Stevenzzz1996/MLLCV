#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/30 11:50


class Solution:
    def merge(intervals):
        n = len(intervals)
        intervals.sort()
        res = []
        i = 0
        while i < n:
            left, right = intervals[i][0], intervals[i][1]
            while i < n-1 and right >= intervals[i+1][0]:   # i必须放前面！
                i += 1
                right = max(right, intervals[i][1])  # 已经加1了！
            res.append([left, right])
            i += 1
        return res
if __name__ == '__main__':
    print(Solution.merge([[1,3],[2,6],[8,10],[15,18]]))