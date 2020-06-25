#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 17:24

# 不保留重复的！
class Solution:
    def deleteDuplicates(self, head: ListNode) -> ListNode:
        dummy = ListNode(-1)
        dummy.next = head
        slow = dummy
        fast = dummy.next
        while fast:
            if fast.next and fast.val == fast.next.val:
                tmp = fast.val  # 用一个tmp记录这个值,如果继续重复，继续跳！！
                while fast and tmp == fast.val:
                    fast = fast.next
            else:
                slow.next = fast
                slow = fast
                fast = fast.next
        slow.next = fast
        return dummy.next


'''
        if head == None or head.next == None:
            return head
        dummy = ListNode(-1)
        dummy.next = head
        slow = dummy
        fast = dummy.next
        while fast:
            while fast.next and slow.next.val == fast.next.val:
                fast = fast.next
            if slow.next == fast:
                slow = fast
            else:
                slow.next = fast.next
            fast = fast.next
        return dummy.next
    '''