#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 14:38


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution:
    def levelOrder(self, root):
        """
        :type root: TreeNode
        :rtype: List[List[int]]
        """
        if not root:
            return []
        res, cur_level = [], [root]
        while cur_level:
            tmp = []
            next_level = []
            for node in cur_level:
                tmp.append(node.val)
                if i.left:
                    next_level.append(node.left)
                if i.right:
                    next_level.append(node.right)
            res.append(tmp)
            cur_level = next_level
        return res
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None
class Solution:
    def levelOrder(self, root: TreeNode) -> List[List[int]]:
        queue = []
        cur = [root]
        while cur:
            cur_layer_val = []
            next_layer_node = []
            for node in cur:
                if node:
                    cur_layer_val.append(node.val)
                    next_layer_node.extend([node.left, node.right])
            if cur_layer_val:
                queue.append(cur_layer_val)
            cur = next_layer_node
        return queue


'''

class Solution:
    def levelOrder(self, root: TreeNode) -> List[List[int]]:
        res=[]
        if not root:
            return res
        def helper(node,level):
            if len(res)==level:  # 给下一个腾出【】
                res.append([])
            res[level].append(node.val)
            if node.left:
                helper(node.left,level+1)
            if node.right:
                helper(node.right,level+1)
        helper(root,0)
        return res       

'''