#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 10:26
# Definition for a binary tree node.

class Solution:
    def levelOrderBottom(self, root):
        """
        先序遍历
        :param root: 根节点
        :return: res -> List
        """
        stack = [root]  # 栈
        res = []  # 先序遍历结果存放列表

        while stack:  # 栈不为空
            node = stack.pop()  # 栈顶节点出栈
            if not node:  # 节点为空
                continue
            res.append(node.val)  # 把不为空的节点数值存到列表
            stack.append(node.right)  # 右节点先压栈
            stack.append(node.left)  # 左节点后压栈
        return res


class TreeNode:
    """
    节点
    """
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

class Solution:
    def levelOrderBottom(self, root):
        """
        中序遍历 非递归
        :param root:  根节点
        :return: res -> List
        """
        stack = []  # 栈
        res = []  # 中序遍历结果存放列表
        p = root  # 当前节点
        while stack or p:  # 当前节点不为空 or 栈不为空
            while p:  # 一直移动到最左端
                stack.append(p)  # 节点压栈
                p = p.left  # 指针左移

            node = stack.pop()  # 出栈
            res.append(node.val)  # 获取节点数据
            p = node.right  # 获取有节点
        return res


# 后序遍历
class Solution:
    def levelOrderBottom(self, root):
        """
        后序遍历 非递归
        :param root: 根节点
        :return: res -> List
        """
        stack = [root]
        res = []
        while stack:
            node = stack.pop()
            if node.left:  # 左孩子不为空
                stack.append(node.left)  # 左孩子压栈
            if node.right:  # 右孩子不为空
                stack.append(node.right)  # 右孩子压栈
            res.append(node.val)  # 获取当前指针数值
        res.reverse()  # 取反
        return res
    

class Solution:
    def levelOrderBottom(self, root):
        """
        层次遍历
        :param root: 根节点
        :return: res -> List 
        """
        queue_node = [root]  # 队列
        res = []  # 中序遍历存放结果列表

        while queue_node:  # 队列不为空,一直循环
            node = queue_node.pop()  # 出队
            if not node:  # 节点为空, 从头开始, 不把空节点放入结果列表
                continue
            res.append(node.val)  # 把节点数值存放到结果列表
            queue_node.insert(0, node.left)  # 左节点先入队
            queue_node.insert(0, node.right)  # 右节点后入队
        return res

