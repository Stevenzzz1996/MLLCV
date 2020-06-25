#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 21:16


# 给定一个头结点为 root 的链表, 编写一个函数以将链表分隔为 k 个连续的部分。
# root = [1, 2, 3], k = 5
#  输出: [[1],[2],[3],[],[]]
class Solution:
    def splitListToParts(self, root: ListNode, k: int) -> List[ListNode]:
        res, stack = [], []
        while root:
            stack.append(root)
            root = root.next
        (p, q) = divmod(len(stack), k)
        j = 0
        for i in range(k):
            if j < len(stack):
                res.append(stack[j])
                j += p + (i < q)
                stack[j - 1].next = None
            else:
                res.append(None)

        return res