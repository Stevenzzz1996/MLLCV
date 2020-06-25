#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/30 10:53

def lastRemaining(n: int, m: int) -> int:
    s = [x for x in range(n)]
    index = m - 1
    while len(s) != 1:
        while index > len(s)-1:  # 防止要删除的索引大于长度
            index -= len(s)
        s.pop(index)  # 去掉该索引
        index += m - 1  # 重新生成索引，注意其始终为m-1，继续往后加啊，怎么可以重新来，索引的引用仍在

    return s[0]

n =10
m = 3
print(lastRemaining(n,m))