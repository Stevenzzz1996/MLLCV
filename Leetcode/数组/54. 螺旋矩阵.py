#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/30 10:52


class Solution:
    def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
        '''
        res = []
        while matrix:
            res += matrix.pop(0)
            matrix = list(map(list, zip(*matrix)))[::-1]
        return res
        '''
        if not matrix : return []
        t = 0
        b = len(matrix) - 1
        l = 0
        r = len(matrix[0]) - 1
        res = []
        while t <= b  and  l <= r:
            # 从左到右
            for i in range(l, r+1):
                res.append(matrix[t][i])
            t += 1
            if t > b:break
            for i in range(t, b+1):
                res.append(matrix[i][r])
            r -= 1
            if l > r:break
            for i in range(r, l - 1,-1):
                res.append(matrix[b][i])
            b -= 1
            # 从下到上
            for i in range(b , t - 1, -1):
                res.append(matrix[i][l])
            l += 1
        return res