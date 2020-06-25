#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 20:40


# 在 O(n log n) 时间复杂度和常数级空间复杂度下，对链表进行排序。
class Solution:
    def sortList(self, head: ListNode) -> ListNode:
        if not head or not head.next:
            return head
        slow, fast = head, head.next
        while fast and fast.next:
            fast, slow = fast.next.next, slow.next
        mid = slow.next
        slow.next = None
        left, right = self.sortList(head), self.sortList(mid)
        pre = dummy = ListNode(0)
        while left and right:
            if left.val < right.val:
                pre.next = left
                left = left.next
            else:
                pre.next = right
                right = right.next
            pre = pre.next
        pre.next = left if left else right
        return dummy.next