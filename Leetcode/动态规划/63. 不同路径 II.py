#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/29 21:46


# 现在考虑网格中有障碍物。
class Solution:
    def uniquePathsWithObstacles(self, obstacleGrid):
        m, n = len(obstacleGrid), len(obstacleGrid[0])
        dp = [[0]*n for _ in range(m)]
        dp[0][0] = 1 if obstacleGrid[0][0] != 1 else 0
        if dp[0][0] == 0: return 0
        for j in range(1, n):
            if obstacleGrid[0][j] != 1:
                dp[0][j] = dp[0][j-1]
        for i in range(1, m):
            if obstacleGrid[i][0] != 1:
                dp[i][0] = dp[i-1][0]
        for i in range(1, m):
            for j in range(1, n):
                if obstacleGrid[i][j] != 1:
                    dp[i][j] = dp[i - 1][j] + dp[i][j-1]

        return dp[-1][-1]
obstacleGrid=[
  [0,0,0],
  [0,1,0],
  [0,0,0]
]
if __name__ == '__main__':
    print(Solution().uniquePathsWithObstacles(obstacleGrid))