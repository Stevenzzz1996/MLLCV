#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 21:24
#
#
# 给定两个用链表表示的整数，每个节点包含一个数位。
#
# 这些数位是反向存放的，也就是个位排在链表首部。
#
# 编写函数对这两个整数求和，并用链表形式返回结果。

class Solution:
    def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
        a, b, p, carry = l1, l2, None, 0
        while a or b:
            val = (a.val if a else 0)+(b.val if b else 0)+carry
            carry, val = val//10 if val >= 10 else 0, val % 10
            p = a if a else b
            p.val = val
            a = a.next if a else None
            b = b.next if b else None
            p.next = a if a else b
        if carry > 0:
            p.next = ListNode(carry)
        return l1