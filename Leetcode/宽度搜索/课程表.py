#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/29 16:42


"""借助一个标志列表 flags，用于判断每个节点 i （课程）的状态：
    未被 DFS 访问：i == 0；
    已被其他节点启动的 DFS 访问：i == -1；
    已被当前节点启动的 DFS 访问：i == 1。
对 numCourses 个节点依次执行 DFS，判断每个节点起步 DFS 是否存在环，若存在环直接返回 False。DFS 流程；
终止条件：
    当 flag[i] == -1，说明当前访问节点已被其他节点启动的 DFS 访问，无需再重复搜索，直接返回 True。
    当 flag[i] == 1，说明在本轮 DFS 搜索中节点 i 被第 22 次访问，即 课程安排图有环 ，直接返回 False。
    将当前访问节点 i 对应 flag[i] 置 11，即标记其被本轮 DFS 访问过；
递归访问当前节点 i 的所有邻接节点 j，当发现环直接返回 False；
当前节点所有邻接节点已被遍历，并没有发现环，则将当前节点 flag 置为 -1−1 并返回 True。
若整个图 DFS 结束并未发现环，返回 True。
"""
from typing import List
def canfinish(numCourses: int, prerequisites: List[List[int]]) -> bool:
    def dfs(i, adjacency, flags):
        if flags[i] == 1: return False
        if flags[i] == -1: return True
        flags[i] = 1
        for j in adjacency[i]:
            if not dfs(j, adjacency, flags):
                return False
        flags[i] = -1
        return True

    adjacency = [[] for _ in range(numCourses)]
    flag = [0 for _ in range(numCourses)]
    for cur, pre in prerequisites:
        adjacency[pre].append(cur)  # 建图

    for i in range(numCourses): # 检测每门功课起始是否存在环
        if not dfs(i, adjacency, flags):
            return False
    return True




# class Solution:
#     def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:
#         from collections import defaultdict
#         graph = defaultdict(list)
#         # 记录
#         visited = set()
#         # 建图
#         for x, y in prerequisites:
#             graph[y].append(x)
#
#         # 深度遍历
#         def dfs(i, being_visited):
#             if i in being_visited: return False
#             if i in visited: return True
#             visited.add(i)
#             being_visited.add(i)
#             for j in graph[i]:
#                 if not dfs(j, being_visited): return False
#             being_visited.remove(i)
#             return True
#         # 检测每门功课起始是否存在环
#         for i in range(numCourses):
#             # 已经访问过
#             if i in visited: continue
#             if not dfs(i, set()): return False
#         return True
