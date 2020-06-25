#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 17:51

# 层次遍历,又称为二叉树的 广度优先搜索（BFS）。
# class Solution:
#     def levelOrder(self, root: TreeNode) -> List[int]:
#         if not root: return []
#         res = []
#
#         def dfs(node, level):
#             if not node:
#                 return
#             if level == len(res):   # 下一层创建一个空[]，【3】，【9，20】，level从0开始！
#                 res.append([])
#             res[level].append(node.val)
#             if node.left: dfs(node.left, level + 1)      #下一层level有了，则append一个【】
#             if node.right: dfs(node.right, level + 1)
#         # 打印
#         dfs(root, 0)
#         final_res = []
#         for i in (res):
#             final_res.extend(i)
#         return final_res

# /从上到下打印出二叉树的每个节点，同一层的节点按照从左到右的顺序打印。


class Solution:
    def levelOrder(self, root: TreeNode) -> List[int]:
        if not root: return []
        res, queue = [], collections.deque()
        queue.append(root)
        while queue:
            node = queue.popleft()
            res.append(node.val)
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
        return res



