#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 18:01

# 保留一个！
class Solution:
    def deleteDuplicates(self, head: ListNode) -> ListNode:
        dummy = ListNode(-1000)
        dummy.next = head
        slow = dummy
        fast = dummy.next
        while fast:
            if slow.val == fast.val:
                fast = fast.next
                slow.next = fast
            else:
                slow = slow.next
                fast = fast.next

        return dummy.next