#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 15:09


class Solution:
    def maxDepth(self, root: TreeNode) -> int:
        if not root: return 0
        return max(self.maxDepth(root.left), self.maxDepth(root.right))+1

#         return max(self.maxDepth(root.left)+1,self.maxDepth(root.right)+1) if root else 0

class Solution:
    def maxDepth(self, root):

        stack = []
        if root: stack.append((1, root))
        depth = 0
        while stack:
            current_depth, root = stack.pop()
            if root:
                depth = max(depth, current_depth)
                stack.append((current_depth + 1, root.left))
                stack.append((current_depth + 1, root.right))

        return depth

class Solution:
    def maxDepth(self, root: TreeNode) -> int:
        # BFS
        if root is None:
            return 0
        queue = [(1, root)]
        while queue:
            depth, node = queue.pop(0)
            if node.left:
                queue.append((depth + 1, node.left))
            if node.right:
                queue.append((depth + 1, node.right))
        return depth


