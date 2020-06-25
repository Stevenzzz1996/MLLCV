#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 21:22


# [1,2,3,4,5,6]
# 输出：此列表中的结点 4 (序列化形式：[4,5,6])
# 由于该列表有两个中间结点，值分别为 3 和 4，我们返回第二个结点。面试题 02.04. 分割链表

class Solution:
    def middleNode(self, head: ListNode) -> ListNode:
        if not head: return 0
        slow, fast = head, head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next

        return slow