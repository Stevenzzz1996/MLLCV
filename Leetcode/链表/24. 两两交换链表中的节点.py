#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 15:55


# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def swapPairs(self, head: ListNode) -> ListNode:
        if not head or not head.next:
            return head
        first_node = head
        second_node = head.next
        first_node.next = self.swapPairs(second_node.next)
        second_node.next = first_node
        return second_node
    '''
        dummy=ListNode(-1)
        dummy.next=head
        pre=dummy
        while head and head.next:
            first=head
            second=head.next
            pre.next=second
            first.next=second.next
            second.next=first
            pre=first
            head=first.next
        return dummy.next
'''