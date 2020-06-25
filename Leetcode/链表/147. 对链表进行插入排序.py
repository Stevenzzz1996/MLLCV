#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 20:27


class Solution:
    def insertionSortList(self, head: ListNode) -> ListNode:
        # 找个排头
        dummy = ListNode(-1)
        pre = dummy
        # 依次拿head节点
        cur = head
        while cur:
            # 把下一次节点保持下来
            tmp = cur.next
            # 找到插入的位置
            while pre.next and pre.next.val < cur.val:
                pre = pre.next
            # 进行插入操作
            cur.next = pre.next
            pre.next = cur
            pre = dummy
            cur = tmp
        return dummy.next
