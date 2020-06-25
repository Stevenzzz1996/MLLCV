#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/6 12:03


# 亚历克斯和李用几堆石子在做游戏。偶数堆石子排成一行，每堆都有正整数颗石子 piles[i] 。
#
# 游戏以谁手中的石子最多来决出胜负。石子的总数是奇数，所以没有平局。
#
# 亚历克斯和李轮流进行，亚历克斯先开始。 每回合，玩家从行的开始或结束处取走整堆石头。
# 这种情况一直持续到没有更多的石子堆为止，此时手中石子最多的玩家获胜。
# 其 中dp[i][j]表示在区间[i, j]内先手拿石子，在理想策略下，可以多拿的石子数

class Solution:
    def stoneGame(self, piles) -> bool:
        n = len(piles)
        dp = [[0] * n for _ in range(n)]  # 能多拿的石子数

        for i in range(n):  # 始化只有i一个石头堆的情形，初始化只需要考虑有一个石头堆的情况，很简单：
            dp[i][i] = piles[i]

        for i in range(n - 1):
            for j in range(n):
                dp[i][j] = max(piles[i] - dp[i + 1][j], piles[j] - dp[i][j - 1])

        return dp[0][n - 1] > 0


if __name__ == '__main__':
    print(Solution().stoneGame([1, 5, 233, 7]))