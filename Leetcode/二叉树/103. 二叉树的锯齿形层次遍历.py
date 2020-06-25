#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 15:01


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution:
    def zigzagLevelOrder(self, root: TreeNode) -> List[List[int]]:
        if not root: return []
        res = []
        cur = [root]
        depth = 0
        while cur:
            tmp = []
            next_level = []
            for node in cur:
                tmp.append(node.val)
                if node.left:
                    next_level.append(node.left)
                if node.right:
                    next_level.append(node.right)
            if depth % 2 == 1:
                res.append(tmp[::-1])
            else:
                res.append(tmp)
            depth += 1
            cur = next_level
        return res