#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 18:26


# 给定一个链表，判断链表中是否有环。
# 用集合
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def hasCycle(self, head: ListNode) -> bool:
        s = set()
        while head:
            if head in s:
                return True
            s.add(head)
            head = head.next
        return False


# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def hasCycle(self, head: ListNode) -> bool:
        l = ListNode(0)
        l.next = head
        r = head
        while l != r:
            if r and r.next:
                r = r.next.next
            else:
                return False
            l = l.next
        return True

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def hasCycle(self, head: ListNode) -> bool:
        if head is None:
            return False
        fast = head
        slow = head
        while fast:
            if fast.next and fast.next.next:
                fast = fast.next.next
                slow = slow.next
            else:
                return False

            if fast == slow:
                return True
        return False

