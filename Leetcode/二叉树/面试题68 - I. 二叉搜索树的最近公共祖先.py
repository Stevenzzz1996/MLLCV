#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 20:03


# 二叉搜索树的性质，利用值的大小来判断！
def lowestCommonAncestor(root, p, q):
    if p.val > q.val:
        p, q = q, p  # 使得p是左子树，q在右子树好判断！
    if p.val == root.val or q.val == root.val:  # 是or
        return root
    if p.val < root.val and q.val > root:
        return root  # 左右两边子树只能定位到根才有可能会重！
    if p.val < root.val and q.val < root.val:
        return lowestCommonAncestor(root.left, p, q)
    if p.val > root.val and q.val > root.val:
        return lowestCommonAncestor(root.right, p, q)

