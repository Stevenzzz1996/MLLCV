#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/1 20:54

class Solution:
    def firstUniqChar(self, s: str) -> str:
        dic = dict()
        for c in s:
            if c in dic:
                dic[c] += 1
            else:
                dic[c] = 1
        for i in dic:
            if dic[i] == 1:
                return i
        return " "

    '''
        n = len(s)
        cnts = [0] * 26
        for i in range(n):
            cnts[ord(s[i]) - 97] += 1
        for i in range(n):
            if cnts[ord(s[i]) - 97] == 1:
                return s[i]
        return " "
    '''
print(("abaccdeff").split(" "))
print(('a b a c c d e f f').split(" "))
for i in range(3):
    s = input().split(" ")
print(s)
