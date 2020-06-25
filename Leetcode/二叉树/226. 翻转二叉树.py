#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 20:47


class Solution:
    def invertTree(self, root: TreeNode) -> TreeNode:
        if not root: return
        root.left, root.right = root.right, root.left
        self.invertTree(root.left)
        self.invertTree(root.right)
        return root