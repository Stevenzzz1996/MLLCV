#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 10:32


def deleteNode(head,val):

    if head.val == val: return head.next
    cur = head

    while cur and cur.next:
        if cur.next.val==val:
            cur.next = cur.next.next
        cur = cur.next
    return head

   # 用了dummy 就可以操作head了，因为dummy还在头这里，而head走到最后了。
   # dummy=ListNode(0)
   # dummy.next=head
   # if head.val==val: return head.next
   #  while head and head.next:
   #     if head.next.val==val:
   #         head.next=head.next.next
   #     head=head.next
   # return dummy.next
