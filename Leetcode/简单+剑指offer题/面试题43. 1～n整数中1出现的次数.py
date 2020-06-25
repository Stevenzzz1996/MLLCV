#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/1 14:08


def countDigitOne(n):
    if n <= 0: return 0
    if n <= 9: return 1
    power = 10**(len(str(n))-1)  # 取几位数
    high = int(str(n)[0])   # 取第一位
    last = int(str(n)[1:])  #  取剩下位
    if high == 1:  # 分两种
        return        countDigitOne(power-1) + countDigitOne(last) + last + 1
    else:
        return high * countDigitOne(power-1) + countDigitOne(last) + power


print(countDigitOne(18))