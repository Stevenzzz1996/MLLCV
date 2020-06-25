#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 20:56


# 定一个单链表，把所有的奇数节点和偶数节点分别排在一起。请注意，这里的奇数节点和偶数节点指的是节点编号的奇偶性，而不是节点的值的奇偶性。
class Solution:
    def oddEvenList(self, head: ListNode) -> ListNode:
        if not head: return
        l1 = head
        tmp = l2 = head.next
        while l2 and l2.next:
            l1.next, l2.next = l1.next.next, l2.next.next
            l1 = l1.next
            l2 = l2.next
        l1.next = tmp  # 拼接
        return head