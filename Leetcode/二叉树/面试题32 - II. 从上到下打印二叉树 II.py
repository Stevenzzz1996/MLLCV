#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 18:22


# 此题res不需要flatten！直接输出即可！
def levelOrder(root) :
    if not root: return []
    res = []
    def bfs(node, level):
        if not node: return
        if level == len(res):
            res.append([])
        res[level].append(node.val)
        if node.left: bfs(node, level+1)
        if node.right: bfs(node, level+1)

    bfs(root, 0)
    return res

# 从上到下按层打印二叉树，同一层的节点按从左到右的顺序打印，每一层打印到一行。
# class Solution:
# def levelOrder(self, root: TreeNode) -> List[List[int]]:
#     if not root: return []
#     res, queue = [], collections.deque()
#     queue.append(root)
#     while queue:
#         tmp = []
#         for _ in range(len(queue)):
#             node = queue.popleft()
#             tmp.append(node.val)
#             if node.left: queue.append(node.left)
#             if node.right: queue.append(node.right)
#         res.append(tmp)
#     return res
