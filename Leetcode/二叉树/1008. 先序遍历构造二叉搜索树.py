#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 10:47


class Solution:
    def bstFromPreorder(self, preorder: List[int]) -> TreeNode:
        if preorder:
            root = TreeNode(preorder.pop(0))
            l, r = [], []
            for i in preorder:
                if i <= root.val:
                    l += [i]
                else:
                    r += [i]
            root.left = self.bstFromPreorder(l)
            root.right = self.bstFromPreorder(r)
            return root