#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 9:18


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution:
    def isBalanced(self, root: TreeNode) -> bool:
        if not root: return True
        if abs(self.height(root.left)-self.height(root.right))>1:
            return False
        else:
            return self.isBalanced(root.left) and self.isBalanced(root.right)
    def height(self,root):
        if not root: return 0
        return 1+max(self.height(root.left), self.height(root.right))
