#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/1 16:21


class Solution:
    import functools
    @functools.lru_cache(None)
    def minCut(self, s: str) -> int:
        if s==s[::-1]: return 0
        res=float('inf')
        for i in range(1,len(s)+1):
            if s[:i]==s[:i][::-1]:
                res=min(self.minCut(s[i:])+1,res)
        return res
if __name__ == '__main__':
    test = Solution()
    print(test.minCut("abcdc"))