#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 21:00


class Solution:
    def binaryTreePaths(self, root: TreeNode) -> List[str]:
        if not root:
            return
        stack = [(root, str(root.val))]
        path = []
        while stack:
            node, tmp = stack.pop()
            if not node.left and not node.right:
                path.append(tmp)
            if node.left:
                stack.append((node.left, tmp+'->'+str(node.left.val)))
            if node.right:
                stack.append((node.right, tmp+'->'+str(node.right.val)))  # 这里tmp还是最开始pop出的！stack存储就是每次的路径！
        return path