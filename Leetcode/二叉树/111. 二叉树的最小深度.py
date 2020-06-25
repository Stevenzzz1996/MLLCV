#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 16:34


class Solution:
    def minDepth(self, root: TreeNode) -> int:
        if not root:
            return 0
        # 4个情况
        if root.left and root.right:
            return min(self.minDepth(root.left), self.minDepth(root.right)) + 1
        elif not root.left and root.right:
            return self.minDepth(root.right) + 1
        elif root.left and not root.right:
            return self.minDepth(root.left) + 1
        else:
            return 1
