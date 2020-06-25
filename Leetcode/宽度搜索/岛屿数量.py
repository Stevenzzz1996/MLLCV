#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/29 15:35
#遍历 grid 当发现 1 辐射出去，找到所有 1
#力扣
def numsIlands(grid):
    if not grid: return 0
    m, n = len(grid), len(grid[0])
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    land = 0

    def isValid(x, y):  # 判断给定坐标是否有效
        return 0 <= x < m and 0 <= y < n
    def dfs(x,y):
        grid[x][y] = "0"
        for d in directions:
            newx, newy = x+d[0], y+d[1]
            if isValid(newx, newy) and grid[newx][newy] == "1":  #岛屿下一块还有，就继续探索，land不变
                dfs(newx, newy)

    for i in range(m):
        for j in range(n):
            if grid[i][j] == "1":
                dfs(i, j)
                land += 1

    return land

grid=[[1,0,0],[0,0,1],[0,0,0]]
print(numsIlands(grid))

#广度优先搜索
# def numIslands(self, grid: List[List[str]]) -> int:
#     from collections import deque
#         if not grid: return 0
#     m, n = len(grid), len(grid[0])
#     directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
#     land = 0
#
#     def bfs(i, j):
#         queue = deque()
#         queue.appendleft((i, j))
#         grid[i][j] = "0"
#         while queue:
#             i, j = queue.pop()
#             for d in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
#                 tmp_i, tmp_j = i+d[0], i+d[1]
#                 if 0 <= tmp_i < row and 0 <= tmp_j < col and grid[tmp_i][tmp_j] == "1":
#                     grid[tmp_i][tmp_j] = "0"
#                     queue.appendleft((tmp_i, tmp_j))
#
#     for i in range(m):
#         for j in range(n):
#             if grid[i][j] == "1":
#                 bfs(i, j)
#                 land += 1
#     return land
