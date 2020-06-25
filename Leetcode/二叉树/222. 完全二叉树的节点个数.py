#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 20:29


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None
# 完全二叉树的定义如下：在完全二叉树中，除了最底层节点可能没填满外，其余每层节点数都达到最大值，并
# 且最下面一层的节点都集中在该层最左边的若干位置。若最底层为第 h 层，则该层包含 1~ 2h 个节点。

class Solution:
    def countNodes(self, root: TreeNode) -> int:
        if not root:
            return 0
        if not root.left and not root.right:
            return 1
        return self.countNodes(root.left) + self.countNodes(root.right) + 1

# class Solution:
    # def countNodes(self, root: TreeNode) -> int:
    #     if not root: return 0
    #     left_height = 0
    #     left_node = root
    #     right_height = 0
    #     right_node = root
    #     while left_node:
    #         left_node = left_node.left
    #         left_height += 1
    #     while right_node:
    #         right_node = right_node.right
    #         right_height += 1
    #     if left_height == right_height:
    #         return pow(2,left_height) - 1  # 填满了！
    #     return 1 + self.countNodes(root.left) + self.countNodes(root.right)