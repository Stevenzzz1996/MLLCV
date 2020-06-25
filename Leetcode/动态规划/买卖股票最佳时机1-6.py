#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/5 15:25


# 最多只能完成一笔交易，即买入和卖出只能进行一次
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        if not prices:
            return 0
        min_price = prices[0]
        max_profit = 0
        n = len(prices)
        for i in range(1, n):
            min_price = min(prices[i], min_price)
            max_profit = max(max_profit, prices[i] - min_price)

        return max_profit


# 次数无限
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        profit = 0
        max_profit = 0
        n = len(prices)
        for i in range(1, n):
            profit = prices[i] - prices[i - 1]
            if profit > 0:
                max_profit += profit
        return max_profit

# 含手续费
class Solution:
    def maxProfit(self, prices: List[int], fee: int) -> int:
        cash, hold = 0, -prices[0]
        for i in range(1, len(prices)):
            cash = max(cash, hold + prices[i] - fee)  # 未持有时的最大利润，可以不变，也可以买入
            hold = max(hold, cash - prices[i])   # 持有时的最大利润，可以不变，也可以买入
        return cash
# class Solution:
#     def maxProfit(self, prices: List[int], fee: int) -> int:
#         # 在卖出之后需要从利润里减去手续费 注意是在卖出的时候 买入的不计算
#         if not prices: return 0
#         n = len(prices)
#         if n < 2: return 0
#         dp = [[0] * 2 for _ in range(n)]
#         dp[0][0] = 0
#         dp[0][1] = -prices[0]
#         for i in range(1, n):
#             dp[i][0] = max(dp[i - 1][0], dp[i - 1][1] + prices[i] - fee)  # 卖出-手续费
#             dp[i][1] = max(dp[i - 1][1], dp[i - 1][0] - prices[i])  # 买入
#         return dp[-1][0]


# 含冷冻期
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        # 每天有持有，卖了未持有，保持未持有三种状态，计算出这三种状态下的最大值，就是最终结果
        # 如果今天持有，那么昨天有两种情况：
        #       1. 昨天持有，今天没有操作
        #       2. 昨天保持未持有，今天买了
        #       不存在昨天卖了未持有，今天买了的情况，因为是冷冻期
        # 在这两种情况下，取最大值，就是今天持有的最大值
        #
        # 如果今天卖了未持有，那么昨天一定是持有状态
        #
        # 如果今天保持未持有，那么昨天有两种情况
        #       1. 昨天卖了未持有，今天没操作
        #       2. 昨天本来未持有，今天没操作
        # 在这两种情况下，取最大值，就是今天未持有的最大值
        #
        # 定义变量p1: 昨天持有的最大收益, p2: 昨天卖了未持有获取的最大收益, p3: 昨天保持未持有获得的最大收益
        # 今天持有的最大收益：p1 = max(p1, p3 - prices[i])
        # 今天卖了未持有的最大收益：p2 = p1 + prices[i]
        # 今天保持未持有的最大收益：p3 = max(p2, p3)

        n = len(prices)
        if n < 2: return 0

        p1, p2, p3 = -prices[0], 0, 0
        for i in range(1, n):
            p1, p2, p3 = max(p1, p3 - prices[i]), p1 + prices[i], max(p2, p3)

        return max(p1, p2, p3)
# class Solution:
#     def maxProfit(self, prices: List[int]) -> int:
#         # dp[i][1] 现在是第i天 持有股票的最大利润
#         # dp[i][0] 现在是第i天 不持有股票的最大利润
#         if not prices: return 0
#         n = len(prices)
#         if n < 2: return 0
#         dp = [[0] * 2 for _ in range(n)]
#         dp[0][0] = dp[1][0] = 0
#         dp[0][1] = -prices[0]
#         for i in range(1, n):
#             dp[i][0] = max(dp[i-1][0], dp[i-1][1] + prices[i])
#             dp[i][1] = max(dp[i-1][1], dp[i-2][0] - prices[i]) # 从卖出（0）到买入 需要1天冷冻期
#         return dp[-1][0]


# 买卖股票的最佳时机3 ，最多可以进行2笔交易

class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        # 2笔
        # 定义卖出股票,交易次数 j + 1
        #  dp[i][j][0] 今天是第i天 进行 j次 交易 手上没有股票
        #  dp[i][j][1] 今天是第i天 进行 j次 交易 手上有股票
        if not prices: return 0
        n = len(prices)
        dp = [[[0] * 2 for _ in range(3)] for _ in range(n)]
        for k in range(3):  # base case i=0
            dp[0][k][0] = 0
            dp[0][k][1] = -prices[0]
        for i in range(1, n):
            for j in range(3):
                if not j:
                    dp[i][j][0] = dp[i-1][j][0]  # 0 base case j=0
                else:
                    dp[i][j][0] = max(dp[i-1][j][0], dp[i-1][j-1][1] + prices[i])
                dp[i][j][1] = max(dp[i-1][j][1], dp[i-1][j][0] - prices[i])
        return max(dp[-1][0][0], dp[-1][1][0], dp[-1][2][0])
# dp[i][j][0]表示当前手上没有股票，这样的状态可以由两个状态转移得来：
# 前一天没有股票，即dp[i-1][j][0]和前一天手上有股票，但卖出去了，即dp[i-1][j][1] + prices[i]
# 这里需要+ prices[i]因为卖出股票会有收益，要时刻记住我们dp的内涵是最大收益鸭。
# 同理，dp[i][j][1] 可以由：dp[i-1][j][1]和前一天没有股票但前一天买入了，即dp[i-1][j-1][0] - prices[i]转移。


# 最多k次
class Solution:
    def maxProfit(self, k: int, prices: List[int]) -> int:
        if not prices:return 0
        if len(prices) < k*2:
            differ = [prices[i]-prices[i-1] for i in range(1,len(prices))]
            return sum([d for d in differ if d>0])
        dp = [[0,0] for i in range(k+1)]
        for i in range(k):
            dp[i][1] = -prices[0]
        for i in range(1,len(prices)):
            for j in range(k,0,-1):
                dp[j][1] = max(dp[j][1],dp[j][0]-prices[i])
                dp[j][0] = max(dp[j][0],dp[j-1][1]+prices[i])
            dp[0][1] = max(dp[0][1],-prices[i])  # 因为是从后往前走，所以实时更新存储第一个位置的最大利润
        return dp[k][0]
'''
        每一天的状态之和前一天的状态有关
        第i次交易的状态之和第i-1次交易的状态有关
        故只存保存前一天的状态，倒序更新即可
        状态转移方程为（1.持有，0.不持有股票）
        持有股票=较大值（前一天持有股票，前一天不持有股票+买入股票）
        dp[j][1] = max(dp[j][1],dp[j][0]-prices[i])
        不持有股票=较大值（前一天不持有股票，前一天持有股票+卖入股票）
        dp[j][0] = max(dp[j][0],dp[j-1][1]+prices[i])
        dp[0][0] = 0(不用更新)
'''


class Solution:
    def maxProfit(self, k: int, prices: List[int]) -> int:
        # 定义卖出股票,交易次数 j + 1
        # dp[i][j][0] 今天是第i天 进行 j次 交易 手上没有股票
        # dp[i][j][1] 今天是第i天 进行 j次 交易 手上有股票
        if k == 0 or len(prices) < 2:
            return 0
        n = len(prices)
        res = []
        if k > n // 2:
            max_profit = 0
            for i in range(1, n):
                profit = prices[i] - prices[i - 1]
                if profit > 0:
                    max_profit += profit
            return max_profit

        dp = [[[0] * 2 for _ in range(k + 1)] for _ in range(n)]
        for i in range(k + 1):
            dp[0][i][0] = 0
            dp[0][i][1] = -prices[0]
        for i in range(1, n):
            for j in range(k + 1):
                if not j:
                    dp[i][j][0] = dp[i - 1][j][0]
                else:
                    dp[i][j][0] = max(dp[i - 1][j][0], dp[i - 1][j - 1][1] + prices[i])  # 在j-1天卖出
                dp[i][j][1] = max(dp[i - 1][j][1], dp[i - 1][j][0] - prices[i])  # 在第j天买

        for m in range(k + 1):
            res.append(dp[-1][m][0])
        return max(res)

