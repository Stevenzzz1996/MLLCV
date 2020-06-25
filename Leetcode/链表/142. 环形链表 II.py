#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 18:29

# 给定一个链表，返回链表开始入环的第一个节点。 如果链表无环，则返回 null。

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def detectCycle(self, head: ListNode) -> ListNode:
        n = set()
        node = head
        while node:
            if node in n:
                return node
            n.add(node)
            node = node.next
        return None


class Solution(object):
    def detectCycle(self, head):
        fast, slow = head, head
        while True:
            if not (fast and fast.next): return
            fast, slow = fast.next.next, slow.next
            if fast == slow: break  # 第一轮相遇，不一定是起点
        fast = head
        while fast != slow:  # 第二轮相遇，一定为起点
            fast, slow = fast.next, slow.next
        return fast
