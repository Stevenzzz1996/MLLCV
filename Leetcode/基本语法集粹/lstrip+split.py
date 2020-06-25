#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/30 14:14


class Solution:
    def lengthOfLastWord(s: str) -> int:

         return len(s.rstrip().split(" ")[-1])
if __name__ == '__main__':
    print(Solution.lengthOfLastWord("Hello World "))