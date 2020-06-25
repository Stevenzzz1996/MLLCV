#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 11:21


# 两个指针，其中一个先走k步，剩下的fast走多少补，就是slow走多少步，slow慢走的步数就是倒数K个步数！

class Solution:
    def getKthFromEnd(self, head: ListNode, k: int) -> ListNode:
        if not head: return
        slow = fast = head
        while k > 0:
            if fast:
                fast = fast.next
            k -= 1
        while fast:
            fast = fast.next
            slow = slow.next
        return slow
