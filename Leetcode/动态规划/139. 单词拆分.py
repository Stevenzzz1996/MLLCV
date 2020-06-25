#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/1 16:09


# 给定一个非空字符串 s 和一个包含非空单词列表的字典 wordDict，判定 s 是否可以被空格拆分为一个或多个在字典中出现的单词。
class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> bool:
        n = len(s)
        dp = [False]*(n+1)
        dp[0] = True
        for i in range(0, n+1):
            for j in range(i+1, n+1):
                if dp[i] and s[i:j] in wordDict:
                    dp[j] = True
        return dp[-1]

# 输入: s = "applepenapple", wordDict = ["apple", "pen"]
# 输出: true
# 解释: 返回 true 因为 "applepenapple" 可以被拆分成 "apple pen apple"。
#      注意你可以重复使用字典中的单词。1·


