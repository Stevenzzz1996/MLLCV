#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 21:43


class Solution:
    def sumNums(self, n: int) -> int:
        def getsum(n):
            sum = n and n + getsum(n-1)
            return sum
        return getsum(n)

    # return n and n + self.sumNums(n - 1)  与运算！
    # return sum(range(1, n + 1))
