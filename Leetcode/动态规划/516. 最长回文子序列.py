#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/29 21:38


#
#class Solution:
#     def longestPalindrome(self, s: str) -> str:
#         if not s:
#             return ""
#         res = ""
#         n = len(s)
#         dp = [[0] * n for _ in range(n)]
#         max_len = float("-inf")
#         for i in range(n):
#             for j in range(i + 1):
#                 if s[i] == s[j] and (i - j < 2 or dp[j + 1][i - 1]):
#                     dp[j][i] = 1
#                 if dp[j][i] and  max_len < i + 1 - j:
#                     res = s[j : i + 1]
#                     max_len = i + 1 - j
#         return res

# def longestPalindrome( s ):
#     max_len, cur_len, start =1, 0, 0
#     n = len(s)
#     dp=[[False] * n for _ in range(n)]
#     for i in range(n):
#         dp[i][i] = True  # 自己到自己都是对的
#     for j in range(1, n):
#         for i in range(j):
#             if s[i] == s[j]:
#                 if j-i < 3:
#                     dp[i][j] = True
#                 else:
#                     dp[i][j] = dp[i+1][j-1]  # 缩小区间
#             else:
#                 dp[i][j] = False
#
#             if dp[i][j]:   # 每一次都要进行判断并更新
#                 cur_len = j-i+1
#                 if max_len < cur_len:
#                     max_len = cur_len
#                     start = i
#     return s[start:start+max_len]
class Solution:
    def longestPalindromeSubseq(self, s: str) -> int:
        n=len(s)
        if n <= 1 or s[::-1] == s: return n
        dp = [[0]*n for _ in range(n)]
        for i in range(n):
            dp[i][i] = 1
        for i in range(n-1, -1, -1):
            for j in range(i+1, n):
                if s[i] == s[j]:
                    dp[i][j] = dp[i+1][j-1]+2
                else:
                    dp[i][j] = max(dp[i+1][j], dp[i][j-1])
        return dp[0][-1]

s = "bdada"
print(longestPalindrome(s))