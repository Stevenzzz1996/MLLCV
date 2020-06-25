#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 19:36


# 锯齿形层次遍历
def levelOrder(root):
    if not root: return []
    res=[]

    def bfs(root,level):
        if not root: return []
        if len(res) == level:
            res.append([])
        if level % 2 == 0:  # 永远往前面加就对了！在0的前面加！相当于逆序了！
            res[level].insert(0, root.val)
        else:  # level是从0开始算的！
            res[level].append(root.val)
        if root.left: bfs(root.left, level+1)
        if root.right: bfs(root, level+1)

    bfs(root, 0)
    return res



# class Solution:
#     def levelOrder(self, root: TreeNode) -> List[List[int]]:
#         if not root: return []
#         res, queue = [], collections.deque()
#         queue.append(root)
#         while queue:
#             tmp = []
#             for _ in range(len(queue)):
#                 node = queue.popleft()
#                 tmp.append(node.val)
#                 if node.left: queue.append(node.left)
#                 if node.right: queue.append(node.right)
#             res.append(tmp[::-1] if len(res) % 2 else tmp)  #也相当于层数为偶数时逆序！！
#         return res
