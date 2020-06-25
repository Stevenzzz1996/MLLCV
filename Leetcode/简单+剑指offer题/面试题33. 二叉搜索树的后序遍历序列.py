#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 19:56


# 左右根,分治
# 判断数组是否为二叉搜索树的后序遍历！
def verifyPostorder(self, postorder: List[int]) -> bool:


    def helper(sequence):
        n = len(sequence)
        if n <= 1: return True
        root = sequence[-1]
        for i in range(n-1):
            if sequence[i]>root:  # 找出大于根的数字，即右子树
                break
        for j in range(i, n-1):  # 遍历右子树，如果发现有小于跟的，返回错！
            if sequence[j]>root:
                return False
        return helper(sequence[:i]) and helper(sequence[i:-1])  #分别进入左右子树判断

    if not postorder: return True
    return helper(postorder)

