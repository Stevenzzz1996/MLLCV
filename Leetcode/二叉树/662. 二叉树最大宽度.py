#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 10:52


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution:
    def widthOfBinaryTree(self, root: TreeNode) -> int:
        if not root:
            return 0
        res = []
        s = [(root, 1, 0)]
        while s:
            cur, num, level = s.pop()
            if cur:
                if level + 1 > len(res):
                    res.append([])
                res[level].append(num)
                s.append((cur.right, 1 + 2 * num, level + 1))
                s.append((cur.left, 2 * num, level + 1))
        val = float('-inf')
        for r in res:
            r.sort()
            val = max(val, r[-1] - r[0] + 1)
        return val
