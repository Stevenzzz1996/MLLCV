#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 11:57

#头就要开始比较，所以需要用一个dummy，比较后再决定连哪个头！

def mergeTwoList(l1,l2):
    dummy = ListNode(0)
    pre = dummy
    while l1 and l2:
        if l1.val < l2.val:
            pre.next = l1
            l1 = l1.next  # 要同步更新！
        else:
            pre.next = l2
            l2 = l2.next
        pre = pre.next  # 要同步更新！
    pre = pre.next if l1 else l2
    return dummy.next


