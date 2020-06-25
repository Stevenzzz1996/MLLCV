#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/5 19:39


# 在一个由 0 和 1 组成的二维矩阵内，找到只包含 1 的最大正方形，并返回其面积。
class Solution:
    def maximalSquare(self, matrix: List[List[str]]) -> int:
        if not matrix: return 0
        res = 0
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if matrix[i][j] == '1':
                    matrix[i][j] = 1
                    if i == 0 or j == 0:  # 第一行，或第一列，因为i，j不能-1
                        res = max(matrix[i][j], res)
                    else:
                        matrix[i][j] = min(matrix[i-1][j], matrix[i-1][j-1], matrix[i][j-1])+1
                        res = max(matrix[i][j], res)  # 每次要记得存下来！
                else:
                    matrix[i][j] = 0
        return res**2


