#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 10:27


# 二叉搜索数的中序遍历最右边就是最大的！
def kthLargest(root, k):
    res = []
    def helper(root):
        if root.left:
            res.append(root.left.val)
        res.append(root.val)
        if root.right:
            res.append(root.right.val)
    helper(root)

    return res[-k]