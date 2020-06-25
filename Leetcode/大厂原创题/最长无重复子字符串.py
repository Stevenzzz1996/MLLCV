#!usr/bin/env python
#-*- coding:utf-8 -*-
#author:  sfhong2020 time:2020/3/28


def lengthOfLongestSubstring(s: str) -> int:
    left=0 #如果开始出现相同的，就从s里面的最左边开始拿掉
    cur_len=0
    max_len=0
    dict=set()#用于存储
    for i in range(len(s)):
        cur_len+=1
        while s[i] in dict:  #如果一直有，继续删除
            dict.remove(s[left])
            cur_len-=1
            left+=1
        if cur_len>max_len:
            max_len=cur_len
        dict.add(s[i])
    return max_len


s = str(input())
s = list(s)
print(lengthOfLongestSubstring(s))