#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 15:37


def spiralOrder(matrix):
    if not matrix: return []
    m, n = len(matrix), len(matrix[0])
    l, r, t, b = 0, n-1, 0, m-1
    res = []
    while l <= r and t <= b:
        for i in range(l, r+1):
            res.append(matrix[t][i])
        t += 1
        if t > b: break   # 特别要注意越界！ 这是终止条件！
        for i in range(t, b+1):
            res.append(matrix[i][r])
        r -= 1
        if l > r: break   # 特别要注意越界！ 这是终止条件！
        for i in range(r, l-1, -1):
            res.append(matrix[b][i])
        b -= 1
        for i in range(b, t-1, -1):
            res.append(matrix[i][l])
        l += 1
    return res

print(spiralOrder(matrix = [[1,2,3,4],[5,6,7,8],[9,10,11,12]]))
