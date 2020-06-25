#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 20:20


def pathSum(root, sum):
    paths = []

    def helper(root, sum, path):
        if not root: return  # 终止条件！
        if not root.left and not root.right:  # 无子树的情况
            if sum == root.val:
                paths.append(path+[root.val])
        if root.left:   # 有左子树，就搜索左子树
            helper(root.left, sum - root.val, path + [root.val])
        if root.righ:   # 有右子树，就搜索右子树
            helper(root.right, sum - root.val, path + [root.val])

    helper(root, sum, [])

    return paths