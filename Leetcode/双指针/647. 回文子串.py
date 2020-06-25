#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/27 19:48


def countSubstrings( S):
    N = len(S)
    ans = 0
    for center in range(2 * N - 1):
        left = center // 2
        right = left + center % 2
        while left >= 0 and right < N and S[left] == S[right]:
            ans += 1
            left -= 1
            right += 1
    return ans

print(countSubstrings("abc"))
# class Solution:
#     def countSubstrings(self, s: str) -> int:
#         def get_Center(s,l,r):
#             count = 0
#             while l>=0 and r<len(s) and s[l]==s[r]:
#                 l-=1
#                 r+=1
#                 count+=1
#             return count
#
#
#         n = len(s)
#         sum1 = 0
#         for i in range(len(s)):
#             count_even = get_Center(s,i,i)
#             count_odd = get_Center(s,i,i+1)
#             sum1 = sum1+count_even+count_odd
#         return sum1