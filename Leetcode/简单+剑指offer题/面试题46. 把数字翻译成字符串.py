#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/1 17:17



def translateNum(num: int) -> int:
    str_num = str(num)
    n = len(str_num)
    dp = [1 for _ in range(n + 1)]
    for i in range(2, n + 1):
        if str_num[i - 2] == '1' or (str_num[i - 2] == '2' and str_num[i - 1] < '6'):
            dp[i] = dp[i - 2] + dp[i - 1]      # 操作的是i-2，i-1，记住, 所以得便利到n+1！看到没这是斐波那契！
        else:
            dp[i] = dp[i - 1]
    return dp[-1]
print(translateNum(1225))
