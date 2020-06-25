#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/28 16:02


class Solution:
    def isMatch(self, s, p):
        sn, pn = len(s), len(p)
        dp = [[False]*(pn+1) for _ in range(sn+1)]
        dp[0][0] = True
        for j in range(1, pn+1):
            if p[j-1] == "*":
                dp[0][j] = dp[0][j-1]
        for i in range(1, sn+1):
            for j in range(1, pn + 1):
                if s[i-1] == p[j-1] or p[j-1] == "?":
                    dp[i][j] = dp[i-1][j-1]
                if p[j-1] == "*":
                    dp[i][j] = dp[i-1][j] or dp[i][j-1]

        return dp[-1][-1]

if __name__ == '__main__':
    test = Solution()
    s = "adceb"
    p = "*a*b"
    print(test.isMatch(s, p))


# class Solution(object):
#     def isMatch(self, s, p):
#         if not p:
#             return not s
#         first=bool(s) and p[0] in {s[0], '?'}
#         if len(p) >= 2 and p[1] == '*':  # 第一个为*的情况继续判断下一个
#             return self.isMatch(s, p[2:]) or first and self.isMatch(s[1:], p)
#         else:
#             return first and self.isMatch(s[1:], p[1:]  # 第一个字母匹配和不匹配的情况。继续判断第二个