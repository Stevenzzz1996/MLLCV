#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/26 22:29


class Solution:
    def maxValue(self, grid: List[List[int]]) -> int:
        m, n = len(grid), len(grid[0])
        for i in range(m):
            for j in range(n):   # 要处理好i为0，j不为0的情况或j为0，i不为0情况！不能直接都取1
                grid[i][j] += max(i > 0 and grid[i - 1][j], j > 0 and grid[i][j - 1])
        return grid[-1][-1]
'''
    def maxValue(grid):
        m, n = len(grid), len(grid[0])
        if not m or not n: return 0
        for i in range(m):
            for j in range(n):
                if i == 0 and j == 0: continue    # 处理边界问题！
                if i == 0:
                    grid[i][j] += grid[i][j - 1]   # 处理边界问题！
                elif j == 0:
                    grid[i][j] += grid[i - 1][j]    # 处理边界问题！
                else:
                    grid[i][j] += max(grid[i][j - 1], grid[i - 1][j])
        return grid[-1][-1]
    '''