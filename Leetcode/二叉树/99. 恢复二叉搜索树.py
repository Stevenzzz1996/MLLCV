#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 12:52

# 二叉搜索树中的两个节点被错误地交换。
#
# 请在不改变其结构的情况下，恢复这棵树。
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution:
    def recoverTree(self, root: TreeNode) -> None:
        """
        Do not return anything, modify root in-place instead.
        """
        firstNode = None
        secondNode = None
        pre = TreeNode(float("-inf"))

        stack = []
        p = root
        while p or stack:
            while p:
                stack.append(p)
                p = p.left
            p = stack.pop()

            if not firstNode and pre.val > p.val:
                firstNode = pre
            if firstNode and pre.val > p.val:
                # print(firstNode.val,pre.val, p.val)
                secondNode = p
            pre = p
            p = p.right
        firstNode.val, secondNode.val = secondNode.val, firstNode.val

# # Definition for a binary tree node.

# # class TreeNode:
# #     def __init__(self, x):
# #         self.val = x
# #         self.left = None
# #         self.right = None
#
# class Solution:
#     def recoverTree(self, root: TreeNode) -> None:
#         """
#         Do not return anything, modify root in-place instead.
#         """
#         self.firstNode = None
#         self.secondNode = None
#         self.preNode = TreeNode(float("-inf"))
#
#         def in_order(root):
#             if not root:
#                 return
#             in_order(root.left)
#             if self.firstNode == None and self.preNode.val >= root.val:
#                 self.firstNode = self.preNode
#             if self.firstNode and self.preNode.val >= root.val:
#                 self.secondNode = root
#             self.preNode = root
#             in_order(root.right)
#
#         in_order(root)
#         self.firstNode.val, self.secondNode.val = self.secondNode.val, self.firstNode.val
#
