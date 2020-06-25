#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/30 14:12



# Definition for a binary tree node.
class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None
from typing import List
class Solution:
    def buildTree(self, preorder: List[int], inorder: List[int]) -> TreeNode:
        if not preorder: return
        root_val = preorder[0]
        root = Treenode(root_val)
        for i in range(len(order)):
            # 找出该索引对应的位置
            # i = inorder.index(root.val)
            if inorder[i] == root_val:
                break
        root.left = self.buildTree(preorder[1:i+1], inorder[:i])
        root.right = self.buildTree(preorder[i+1:], inorder[i+1:])
        return root
if __name__ == '__main__':
    preorder = [3, 9, 20, 15, 7]
    inorder = [9, 3, 15, 20, 7]
    print(buildTree(preorder, inorder))
