#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/30 20:55


# 每一步只能移动到下一行中相邻的结点上。
#
# 相邻的结点 在这里指的是 下标 与 上一层结点下标 相同或者等于 上一层结点下标 + 1 的两个结点。
class Solution:
    def minimumTotal(self, triangle) -> int:
        if not triangle: return 0
        m = len(triangle)  # n不能直接初始化了！
        if m == 1: return triangle[0][0]
        for i in range(1, m):  # 注意这里只原位操作到最后一行，然后就没了，最后要返回最后一行的最小值，与开辟新矩阵有区别！
            for j in range(len(triangle[i])):
                if j == 0:
                    triangle[i][j] += triangle[i-1][j]
                elif j == len(triangle[i])-1:
                    triangle[i][j] += triangle[i-1][j-1]
                else:
                    triangle[i][j] += min(triangle[i-1][j], triangle[i-1][j-1])
        return min(triangle[-1])


triangle = [
     [2],
    [3,4],
   [6,5,7],
  [4,1,8,3]
]
if __name__ == '__main__':
    print(Solution().minimumTotal(triangle))