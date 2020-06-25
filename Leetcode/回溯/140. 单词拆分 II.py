#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/3 18:52


from typing import List
class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> List[str]:
        import functools
        if not wordDict:return []
        wordDict = set(wordDict)
        max_len = max(map(len, wordDict))
        @functools.lru_cache(None)
        def helper(s):
            res = []
            if not s:
                res.append("")
                return res
            for i in range(len(s)):
                if i < max_len and s[:i+1] in wordDict:
                    for t in helper(s[i+1:]):
                        if not t:
                            res.append(s[:i+1])
                        else:
                            res.append(s[:i+1] + " " + t)
            return res
        return helper(s)
s = "catsanddog"
wordDict = ["cat", "cats", "and", "sand", "dog"]
if __name__ == '__main__':
    print(Solution().wordBreak(s,wordDict))