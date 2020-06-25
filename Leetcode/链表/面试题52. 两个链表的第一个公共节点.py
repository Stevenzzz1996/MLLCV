#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 9:18


def getIntersectionNode(headA, headB):
    if not headA or not headB: return
    l1,l2 = headA, headB
    while l1 != l2:   # 注意是地址相同不是值相同！
        l1 = l1.next if l1 else headB
        l2 = l2.next if l2 else headA
    return l1    # 跳出循环的时候就是公共！
