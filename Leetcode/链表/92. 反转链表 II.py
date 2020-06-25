#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 18:10


# 反转从位置 m 到 n 的链表。请使用一趟扫描完成反转。
class Solution:
    def reverseBetween(self, head: ListNode, m: int, n: int) -> ListNode:
        '''
        dummy = ListNode(0)
        cur, num = dummy, 1
        while num < m:
            cur.next = head
            head = head.next
            cur = cur.next
            cur.next = None
            num += 1
        while num <= n:
            p = head
            head = head.next
            p.next = cur.next
            cur.next = p
            num += 1
        while cur.next:
            cur = cur.next
        cur.next = head
        return dummy.next
        '''

        dummy = ListNode(-1)
        dummy.next = head
        pre = dummy
        # 找到翻转链表部分的前一个节点, 1->2->3->4->5->NULL, m = 2, n = 4 指的是 节点值为1
        for _ in range(m-1):
            pre = pre.next
        # 用双指针,进行链表翻转
        node = None
        cur = pre.next
        for _ in range(n-m+1):
            tmp = cur.next
            cur.next = node
            node = cur
            cur = tmp
        # 将翻转部分 和 原链表拼接
        pre.next.next = cur
        pre.next = node
        return dummy.next
