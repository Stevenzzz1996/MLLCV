#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 13:46


class Solution:
    def mirrorTree(self, root: TreeNode) -> TreeNode:
        if not root: return
        root.left,root.right=root.right,root.left
        self.mirrorTree(root.left)
        self.mirrorTree(root.right)

        return root