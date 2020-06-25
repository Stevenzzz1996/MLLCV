#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 11:35


def reverseList(self, head: ListNode) -> ListNode:
    pre = None
    cur = head
    while cur:
        tmp = cur.next
        cur.next = pre  # 切断！
        pre = cur  #更新
        cur = tmp

    return pre


'''
    # 边界判断，妙啊
    if not head or not head.next:  return head
    cur = self.reverseList(head.next)
    head.next.next = head
    head.next = None
    return cur
'''