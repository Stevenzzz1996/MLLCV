#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 19:20


class Solution:
    def reverseLeftWords(self, s: str, n: int):
        return s[n:] + s[:n]