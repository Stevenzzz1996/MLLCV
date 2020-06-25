#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 21:26


# 给定一棵二叉树，设计一个算法，创建含有某一深度上所有节点的链表
# （比如，若一棵树的深度为 D，则会创建出 D 个链表）。返回一个包含所有深度的链表的数组。
class Solution:
    def listOfDepth(self, tree: TreeNode) -> List[ListNode]:
        if not tree: return
        stack = [tree]
        res = []
        while stack:
            n = len(stack)
            head = ListNode(None)
            cur = head
            for i in range(n):
                node = stack.pop(0)
                if node.left:
                    stack.append(node.left)
                if node.right:
                    stack.append(node.right)
                cur.next = ListNode(node.val)
                cur = cur.next
            res.append(head.next)
        return res