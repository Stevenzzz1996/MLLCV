#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/12 16:54


s=str(input())
def matchstick(s):
    dict={"0":"8", "1":"7", "3":"9","5":"9","6":"8" }
    lookup = {}
    for i in range(len(s)):
        if all(s[i] not in dict):
            return -1
    if s[i] in dict:

