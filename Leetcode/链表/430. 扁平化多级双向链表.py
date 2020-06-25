#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 21:13


"""
# Definition for a Node.
class Node:
    def __init__(self, val, prev, next, child):
        self.val = val
        self.prev = prev
        self.next = next
        self.child = child
"""
class Solution:
    def flatten(self, head: 'Node') -> 'Node':
        p = res = Node(None,None,None,None) ## 初始化结果链表及其指针
        visited = head and [head] ## 初始化栈
        while visited:
            vertex = visited.pop()
            if vertex.next: visited.append(vertex.next)
            if vertex.child: visited.append(vertex.child)
            p.next= vertex ## pop出来的节点就是所需节点
            p, p.prev, p.child = p.next, p, None ## 设定节点属性
        if res.next: res.next.prev = None ## res.next的prev属性要设为None
        return res.next