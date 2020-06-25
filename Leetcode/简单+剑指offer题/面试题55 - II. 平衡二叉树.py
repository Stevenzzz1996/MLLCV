#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 10:54


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution:  # 先执行根的左右子树是否《=1，然后继续判断左子树和右子树各自，往下递归！
    def isBalanced(self, root: TreeNode) -> bool:
        if not root: return True
        return abs(self.height(root.left) - self.height(root.right)) <= 1 and \
             self.isBalanced(root.left) and self.isBalanced(root.right)
    def height(self, root):
        if not root: return 0
        return 1+max(self.height(root.left), self.height(root.right))  # 求最深的深度即为该子树最终的深度
