#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 13:46


def mirrorTree(self, root: TreeNode) -> TreeNode:
    if not root: return
    root.left, root.right = root.right, root.left
    mirrorTree(root.left)  # 作为各自的跟继续寻找！
    mirrorTree(root.right)
    return root