#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/29 17:55


# 直接从左往右加就完事了

def addTwoNumber(l1, l2) :
    a, b, p, carry = l1, l2, None, 0
    while a or b:
        val = (a.val if a else 0) + (b.val if b else 0) + carry
        carry = val // 10
        val = val % 10
        p = a if a else b
        p.val = val
        a = a.next if a else None
        b = b.next if b else None
        p = p.next if a else b
    if carry > 0:
        p.next = ListNode(carry)
    return a

l1=(2 , 4 , 3)
l2=(2 , 4 , 3)
print(addTwoNumber(l1,l2))