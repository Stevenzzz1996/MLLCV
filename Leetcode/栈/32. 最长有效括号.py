#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/28 15:48


class Solution:
    def longestValidParentheses(s):
        if not s:
            return 0
        res = 0
        stack = [-1]
        for i in range(len(s)):
            if s[i] == "(":
                stack.append(i)
            else:
                stack.pop()
                if not stack:  # 防止一直出现）报错，就把i加进来再pop！
                    stack.append(i)
                else:
                    res = max(res, i-stack[-1])
        return res

if __name__ == '__main__':
    print(Solution.longestValidParentheses("))()())"))
