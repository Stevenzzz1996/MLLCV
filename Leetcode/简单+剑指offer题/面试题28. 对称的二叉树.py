#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 15:20


def isSymetric(root):

    def helper(p1, p2):
        if not p1 and not p2: return True
        if not p1 or not p2: return False
        return p1.val == p2.val and helper(p1.left, p2.right) \
               and helper(p1.right, p2.left)

    if not root: return True
    return helper(root.left, root.right)


