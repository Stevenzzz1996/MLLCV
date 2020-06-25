#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/30 20:20


class Solution:
    def numDecodings(self, s):
        n = len(s)
        if not s or s[0] == "0": return 0
        dp = [0]*(n+1)
        dp[0] = dp[1] = 1
        for i in range(1, n):
            if s[i] == "0":
                if "0" < s[i-1] <= "2":
                    dp[i+1] = dp[i-1]
                else:
                    return 0
            else:
                if s[i-1] == "1" or (s[i - 1] == "2" and "1" <= s[i] <= "6"):
                    dp[i + 1] = dp[i] + dp[i - 1]
                else:
                    dp[i+1] = dp[i]
        return dp[-1]


if __name__ == '__main__':
    print(Solution().numDecodings('227'))