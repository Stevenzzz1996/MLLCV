#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 20:38


# ^：匹配字符串开头
# [\+\-]：代表一个+字符或-字符
# ?：前面一个字符可有可无
# \d：一个数字
# +：前面一个字符的一个或多个
# \D：一个非数字字符
# *：前面一个字符的0个或多个
# 这个星号虽然放在re的前面，但是它和re或者re.findall并没有直接的关系，相反，和它有关的是int
# i = int(*re.findall('^[\+\-]?\d+', s.lstrip()))
# 相当于result = re.findall('^[\+\-]?\d+', s.lstrip())
# i = int(*result)
# 这个result是一个列表，而int接受的是单个的参数，所以需要通过*的unpack运算将它转换为元组。
# int(*result)其实就是 int(result[0])
import re
class Solution:
    def strToInt(self, str: str) -> int:
        return max(min(int(*re.findall('^[\+\-]?\d+',str.lstrip())), 2**31-1), -2**31)

print("  sf  1".lstrip())  # 去掉前面的空格
