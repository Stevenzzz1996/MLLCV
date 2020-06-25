#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/1 14:41


# 那么给定位数，可以根据以上规律求得第n个字符数对应的整数，以及对应整数拥有的位数。
#
# 例如对于n=999，999小于3位的字符数累积总和（2889），大于2位的字符数累积总和（189），
# 说明其对应数字的位数为3。
# 随后999-189 - 1 = 809,说明其位于3位数中的第809个字符
# div, mod = divmod(809, 3) # div=269, mod = 2
# 说明其对应的整数为100 + 269 = 369, mod=2 即取369的第2个数，故最后答案为9

def findNthDigit(n):
    num = 9
    digit = 1
    while n-num*digit > 0:
        n -= num*digit
        num *= 10
        digit += 1   # 此时n已经剪掉了前面2位数的个数
    div, mod = divmod(n, digit)   # 这里就是得到第三位数的第几个
    return int(str(10*(digit-1)+div)[mod])
print(findNthDigit(999))



