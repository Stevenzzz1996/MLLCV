#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 9:26


# Definition for a binary tree node.
class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

# 递归
class Solutio:
    def isValidBST(self, root:TreeNode) -> bool:
        nodes = []
        def search(root):
            if root:
                search(root.left)
                nodes.append(root.val)
                search(root.right)
        search(root)
        return nodes == sorted(set(nodes))

# 非递归
class Solution1:
    def isValidBST(self, root:TreeNode) -> bool:
        stack = []
        p = root
        res = []

        while p or stack:
            while p:
                stack.append(p)
                p = p.left

            if stack:
                node = stack.pop()
                res.append(node.val)
                p = node.right

        return res == sorted(set(res))
if __name__ == '__main__':
    print(Solution().isValidBST( [5,1,4,3,6]))


#
class Solution:
    def isValidBST(self, root: TreeNode) -> bool:
        def helper(node,lower = float('-inf'), upper = float('inf')):
            if not node:
                return True
            if node.val<=lower or node.val>=upper:
                return False
            if not helper(node.right,node.val,upper):
                return False
            if not helper(node.left,lower,node.val):
                return False
            return True
        return helper(root)
