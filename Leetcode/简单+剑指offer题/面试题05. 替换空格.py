#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/30 13:17


def replaceSpace(s:str) -> str:
    # s=s.replace(" ","%20")
    # return s
    #重建s1
    s1 = ""
    for ch in s:
        if ch == " ":
            s1 += "%20"
        else:
            s1 += ch
    return s1


s = "We are happy."
print(replaceSpace(s))
