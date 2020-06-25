#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 14:51


class Solution:
    def isSymmetric(self, root: TreeNode) -> bool:
        if not root:
            return True
        def dfs(left,right):
            if  (left==None and right==None):  # 00
                return True
            if not (left and right):  # 01，10，可写成not left or not right
                return False
            if left.val != right.val:
                return False
            return dfs(left.left, right.right) and dfs(left.right, right.left)
        return dfs(root.left, root.right)