#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 20:55


class Solution:
    def constructArr(self, a: List[int]) -> List[int]:
        if not a:  return
        pre = [1]*len(a)
        pre[0] = 1
        for i in range(1, len(a)):
            pre[i] = pre[i-1]*a[i-1]
        cur = 1
        for i in range(len(a)-1, -1, -1):
            pre[i] = pre[i] * cur
            cur *= a[i]
        return pre