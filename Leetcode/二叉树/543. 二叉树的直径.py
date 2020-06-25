#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 10:22


# 一棵二叉树的直径长度是任意两个结点路径长度中的最大值。这条路径可能穿过也可能不穿过根结点。两结点之间的路径长度是以它们之间边的数目表示！！

class Solution:
    def __init__(self):
        self.max = 0

    def diameterOfBinaryTree(self, root: TreeNode) -> int:
        def depth(self, root):
            if not root:
                return 0
            l = self.depth(root.left)
            r = self.depth(root.right)
            self.max = max(self.max, l + r)
            return max(l, r) + 1

        depth(root)
        return self.max