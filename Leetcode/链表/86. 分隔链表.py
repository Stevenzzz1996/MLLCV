#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 18:08


# 给定一个链表和一个特定值 x，对链表进行分隔，使得所有小于 x 的节点都在大于或等于 x 的节点之前。
class Solution:
    def partition(self, head: ListNode, x: int) -> ListNode:
        before = before_head = ListNode(0)
        after = after_head = ListNode(0)
        while head:
            if head.val < x:
                before.next = head
                before = before.next
            else:
                after.next = head
                after = after.next

            head = head.next
        after.next = None
        before.next = after_head.next

        return before_head.next