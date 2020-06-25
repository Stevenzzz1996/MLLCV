#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 10:34


#方法1：先序遍历
# 常见的 DFS ： 先序遍历、中序遍历、后序遍历；
# 常见的 BFS ： 层序遍历（即按层遍历）。
def maxDepth(root):
    if not root: return 0  # 终止条件：当 root​为空，说明已越过叶节点，因此返回 深度 00 。
    return 1+max(maxDepth(root.left), maxDepth(root.right))


# 方法二：层序遍历（BFS）
# 树的层序遍历 / 广度优先搜索往往利用 队列 实现。
# 关键点： 每遍历一层，则计数器 +1 ，直到遍历完成，则可得到树的深度。

def maxDepth(root):
    if not root: return 0
    queue = [root]
    res = 0
    while queue:
        tmp = []
        for node in queue:
            if root.left: queue.append(node.left)
            if root.right: queue.append(node.right)
        queue = tmp
        res += 1      # 最后queue在tmp为叶子节点时又遍历了一次！所以最开始res=0！

    return res