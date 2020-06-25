#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 21:32


# 只能用异或计算！
class Solution:
    def add(a: int, b: int) -> int:
        '''
        return sum([a,b])
        '''
        carry = 1
        while carry:
            s = a ^ b
            carry = 0xFFFFFFFF & ((a & b) << 1)
            carry = -(~(carry - 1) & 0xFFFFFFFF) if carry > 0x7FFFFFFF else carry
            a = s
            b = carry
        return a

if __name__ == '__main__':
    print(Solution.add(14, 7))
