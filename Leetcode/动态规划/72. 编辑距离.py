#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/25 15:33


# dp[i][j] 代表 word1 到 i 位置转换成 word2 到 j 位置需要最少步数
#
# 当 word1[i] == word2[j]，dp[i][j] = dp[i-1][j-1]；
#
# 当 word1[i] != word2[j]，dp[i][j] = min(dp[i-1][j-1], dp[i-1][j], dp[i][j-1]) + 1
#
# 其中，dp[i-1][j-1] 表示替换操作，dp[i-1][j] 表示删除操作，dp[i][j-1] 表示插入操作。
# 行增，列删，斜改
class Solution:
    def minStance(self, str1, str2):
        m, n = len(str1), len(str2)
        dp = [[0] * (n+1) for _ in range(m+1)]
        for i in range(1, m + 1):  # 所有行的第一列全部进行增
            dp[i][0] = dp[i-1][0]+1
        for j in range(1, n + 1):  # 第一行全部进行删除
            dp[0][j] = dp[0][j-1]+1

        for i in range(1, m+1):
            for j in range(1, n+1):
                if str1[i-1] == str2[j-1]:  # 当前相同就用之前的！字符是从0开始的！而dp是从1操作的
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
                    # 配合增删改这三种操作，需要对应的 dp 把操作次数加一，取三种的最小
        return dp[-1][-1]

str1 = "horse"
str2 = "ros"
if __name__ == '__main__':
    print(Solution().minStance(str1, str2))