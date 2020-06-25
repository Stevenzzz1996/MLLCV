#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 18:24


# 给定一个单链表，其中的元素按升序排序，将其转换为高度平衡的二叉搜索树。
class Solution:
    def sortedListToBST(self, head: ListNode) -> TreeNode:
        def findmid(head, tail):
            slow = head
            fast = head
            while fast != tail and fast.next != tail:
                slow = slow.next
                fast = fast.next.next
            return slow

        def helper(head, tail):
            if head == tail: return
            node = findmid(head, tail)
            root = TreeNode(node.val)
            root.left = helper(head, node)
            root.right = helper(node.next, tail)
            return root

        return helper(head, None)