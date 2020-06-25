#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 18:05


def reverseWords(self, s: str) -> str:
    return " ".join(s.split()[::-1])  # 先用空格划分单词反转后再用空格拼接回来！
