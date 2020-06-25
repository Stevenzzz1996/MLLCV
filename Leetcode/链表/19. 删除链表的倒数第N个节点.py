#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 15:18

class Solution:
    def removeNthFromEnd(self, head: ListNode, n: int) -> ListNode:
        if not head: return
        dummy = ListNode(0)
        dummy.next = head
        fast = dummy
        while n:
            fast = fast.next  # fast先走n步
            n -= 1
        slow = dummy
        while fast and fast.next:
            fast = fast.next  # fast到达最后slow也就到了倒数第n补！
            slow = slow.next
        slow.next = slow.next.next  # 删除第n个！

        return dummy.next   # 直接返回头节点！