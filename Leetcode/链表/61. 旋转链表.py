#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 16:50


# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None
# 用双指针找到倒数k+1个数，然后直接反转
class Solution:
    def rotateRight(self, head: ListNode, k: int) -> ListNode:
        if not head: return head
        n = 0
        cur = head
        while cur:
            cur = cur.next
            n += 1
        k %= n

        first = second = head
        for i in range(k, 0, -1):
            first = first.next

        while first.next:
            first = first.next
            second = second.next

        first.next = head
        head = second.next
        second.next = None
        return head


class Solution:
    def rotateRight(self, head: ListNode, k: int) -> ListNode:
        if not head or not head.next or not k: return head
        num = 0
        dummy = ListNode(0)
        dummy.next = head
        p1 = dummy
        p2 = dummy
        while p1.next:
            num += 1
            p1 = p1.next

        k = num - k % num
        while k:
            p2 = p2.next
            k -= 1
        p1.next = dummy.next
        dummy.next = p2.next
        p2.next = None
        return dummy.next