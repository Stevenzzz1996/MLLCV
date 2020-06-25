#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 20:20


# 给定一个单链表 L：L0→L1→…→Ln-1→Ln ，
# 将其重新排列后变为： L0→Ln→L1→Ln-1→L2→Ln-2→…
#
# 你不能只是单纯的改变节点内部的值，而是需要实际的进行节点交换。

class Solution:
    def reorderList(self, head: ListNode) -> None:
        """
        Do not return anything, modify head in-place instead.
        """
        if not head: return
        stack = []
        pre = head
        while pre:
            stack.append(pre)
            pre = pre.next
        count = (len(stack) - 1) // 2
        pre = head
        while count:
            tmp = stack.pop()
            tmp.next = pre.next
            pre.next = tmp

            pre = tmp.next
            count -= 1

        stack.pop().next = None