#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 17:40

# 本题中，路径被定义为一条从树中任意节点出发，达到任意节点的序列。该路径至少包含一个节点，且不一定经过根节点。
def maxPathSum(self, root: TreeNode) -> int:
    self.res = float("-inf")

    def helper(root):
        if not root: return 0
        # 左边最大值
        left = helper(root.left)
        # 右边最大值
        right = helper(root.right)
        # 和全局变量比较
        self.res = max(left + right + root.val, self.res)
        # > 0 说明都能使路径变大
        return max(0, max(left, right) + root.val)

    helper(root)
    return self.res
