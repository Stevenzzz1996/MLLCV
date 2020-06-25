#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/5 21:29


class Solution:
    def oneEditAway(self, first: str, second: str) -> bool:
        if first == second: return True
        if abs(len(first)-len(second)) > 1:
            return False
        i, j = 0, 0
        cnt = 0
        while i < len(first) and j < len(second):
            if first[i] == second[j]:
                i += 1
                j += 1
            else:
                cnt += 1
                if len(second) == len(first)+1:
                    j += 1
                elif len(first) == len(second):
                    i += 1
                    j += 1
                else:
                    i += 1
        if cnt > 1:
            return False
        return True

'''
0次编辑 -> 字符串相等
1次编辑 ->
删除 -> len(sec) = len(first) + 1, 比较过程可跳过一个字母
插入 -> len(sec) = len(first) - 1, 比较过程可跳过一个字母
替换 -> len(sec) = len(first)，比较过程可跳过一个字母

对应字符串的比较会使用双指针算法，那么由于删除、插入、替换在比较过程汇总均可以跳过一个字母，
只  需  要在比较不相等时根据字符串长度来判断应执行哪个操作即可。
'''