#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 21:35


# 一个树的节点的坡度定义即为，该节点左子树的结点之和和右子树结点之和的差的绝对值。空结点的的坡度是0。
#
# 整个树的坡度就是其所有节点的坡度之和。
class Solution:
    def findTilt(self, root: TreeNode) -> int:
        res = 0
        def dfs(root):
            if not root: return 0
            nonlocal res
            left = dfs(root.left)
            right = dfs(root.right)
            res += abs(left-right)
            return root.val+left+right
        dfs(root)
        return res