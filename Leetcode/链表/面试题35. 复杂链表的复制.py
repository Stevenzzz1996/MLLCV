#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 21:54

class Solution:
    def copyRandomList(self, head: 'Node') -> 'Node':
        if not head: return
        # 复制节点
        cur = head
        while cur:
            tmp = cur.next
            cur.next = Node(cur.val, None, None)  # 创建一个开始的节点
            cur.next.next = tmp  # 拼接1'和2
            cur = tmp  # 更新
        # 复制random节点
        cur = head
        while cur:
            if cur.random:   # 得判断是否有随机指针！
                cur.next.random = cur.random.next
            cur = cur.next.next  # 更新
        # 拆分
        cur = head
        copy_head = cur.next
        copy_cur = copy_head
        while copy_cur.next:
            cur.next = cur.next.next  # 自己连自己的
            cur = cur.next  # 更新
            copy_cur.next = copy_cur.next.next  # 自己连自己的
            copy_cur = copy_cur.next  # 更新

        #  把链表结束置空
        cur.next = None
        copy_cur.next = None
        return copy_head


