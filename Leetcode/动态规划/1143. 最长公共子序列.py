#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/25 11:43

"""
典型的动态规划
        dp[i][j]表示text1前i个字符与text2前j个字符的最大公共子串
        分析字符串的状态转移
        dp[i-1][j] ->dp[i][j]表示text1增加一个字符，text2不增加
        dp[i][j-1] ->dp[i][j]表示text2增加一个字符，text1不增加
        dp[i-1][j-1] ->dp[i][j] 表示text1和text2同时+1个字符。
        状态转移方程如下：
        当text1[i] == text2[j] 时，dp[i][j] = dp[i-1][j-1]+1;
        当text1[i] != text2[j] 时，dp[i][j] = max(dp[i-1][j],dp[i][j-1]，dp[i-1][j-1]);
        很多解法省略了text1[i] != text2[j] 时，取最大值要包含dp[i-1][j-1]，
        不是很好理解。我在这里加上了，表示状态转移的完备性
        （可以省略掉的原因：由于dp[i-1][j]和dp[i][j-1]比dp[i-1][j-1]多一个字母，
        因此dp[i-1][j-1]一定小于等于两者的最小值）
"""
#
# def longestCommonSubsequence(str1,str2):
#     m,n = len(str1),len(str2)
#     dp = [[0] * (n+1) for _ in range(m+1)]
#     for i in range(1,m+1):
#         for j in range(1,n+1):
#             if str1[i-1] == str2[j-1]:
#                 dp[i][j] = dp[i-1][j-1]+1
#             else:
#                 dp[i][j] = max(dp[i-1][j], dp[i][j-1])
#     return dp[-1][-1]
#
# str1 = "abcde"
# str2 = "ace"
# if __name__ == '__main__':
#     print(longestCommonSubsequence(str1, str2))

import numpy as np

def longest_common_subsequence(lhs, rhs):
    l_len = len(lhs)
    r_len = len(rhs)
    matrix = np.zeros((l_len, r_len))
    for i in range(l_len):
        for j in range(r_len):
            if lhs[i] == rhs[j]:
                if i != 0 and j != 0:
                    matrix[i][j] = matrix[i-1][j-1]+1
                else:
                    matrix[i][j] = 1
            elif i != 0 and j != 0:
                    matrix[i][j] = max(matrix[i-1][j], matrix[i][j-1])
    return matrix[-1][-1]
str1 = "abcde"
str2 = "ace"
print(longest_common_subsequence(str1, str2))