#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/1 20:11


# 滑动窗口
def lengthOfLongestSubstring(s: str) -> int:
    lookup = set()
    left = 0
    max_len = 0
    cur_len = 0
    if not s: return 0
    for i in range(len(s)):
        cur_len += 1
        while s[i] in lookup:
            lookup.remove(s[left])
            cur_len -= 1
            left += 1
        if cur_len > max_len:
            max_len = cur_len
        lookup.add(s[i])   # 一定要放到最后，不管咋样直接加进来，先i下一轮就是判断I+1在不在！
    return max_len

s = "abcabcbb"
print(lengthOfLongestSubstring(s))