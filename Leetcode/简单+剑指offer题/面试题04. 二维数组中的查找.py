#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/30 12:10

# 从右上角开始找，或左下角开始也可以。
from typing import List
def findNumberIn2DArray(matrix: List[List[int]], target: int) -> bool:
    if not matrix: return False
    m, n = len(matrix), len(matrix[0])
    x = 0
    y = n-1
    while y >= 0 and x < m:
            if target > matrix[x][y]:
                x += 1
            elif target < matrix[x][y]:
                y -= 1
            else:
                return True
    return False

matrix=[
  [1,   4,  7, 11, 15],
  [2,   5,  8, 12, 19],
  [3,   6,  9, 16, 22],
  [10, 13, 14, 17, 24],
  [18, 21, 23, 26, 30]
]

print(findNumberIn2DArray(matrix, target=5))

