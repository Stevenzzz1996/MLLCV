#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/6 10:24


# 设想有个机器人坐在一个网格的左上角，网格 r 行 c 列。机器人只能向下或向右移动，但不能走到一些被禁止的网格（有障碍物）。
# 设计一种算法，寻找机器人从左上角移动到右下角的路径。

# 网格中的障碍物和空位置分别用 1 和 0 来表示。
#
# 返回一条可行的路径，路径由经过的网格的行号和列号组成。左上角为 0 行 0 列。如果没有可行的路径，返回空数组。

class Solution:
    def pathWithObstacles(self, obstacleGrid):
        m, n = len(obstacleGrid), len(obstacleGrid[0])
        if m == 0 or n == 0: return []
        res = []
        def dfs(path):
            if not res:
                i, j = path[-1]
                if obstacleGrid[i][j] == 0:
                    obstacleGrid[i][j] = 1  # 走过的不能再走了！
                    i < m-1 and dfs(path+[[i+1, j]])
                    j < n-1 and dfs(path+[[i, j+1]])
                    if (i, j) == (m-1, n-1):
                        res.extend(path)  # extend是将一行一列添加，而append是所有行添加完了再添加列！这里因为是dfs!
        dfs([[0, 0]])
        return res
obstacleGrid=[
  [0,0,0],
  [0,1,0],
  [0,0,0]
]

if __name__ == '__main__':
    print(Solution().pathWithObstacles(obstacleGrid))
