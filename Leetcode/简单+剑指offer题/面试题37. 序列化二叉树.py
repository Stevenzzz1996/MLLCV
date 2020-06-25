#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/1 10:02


# 序列化就是层次/先序/中序/后序/遍历。
# 反序列化建立节点列表，与输入的值列表配合判断。
# 编码：先序遍历，需要注意的是，在遇到空节点时，我们要把一个None加入到序列中
# 解码：递归解码，solve(data, i)寻找data中从位置i开始的部分序列所构成的子树，它的返回值为(root, k)，
# root为子树的根，k为下一个子树所对应的序列的起点，也就是i+当前子树的节点数(包含空的叶子节点)。
# 从前往后遍历序列，如果当前元素为空，则返回空树，并令当前位置+1；
# 否则返回以当前元素为根的子树：首先用当前元素的值建立根节点，然后依次建立左右子树：
# 先令当前位置i=i+1，并从当前位置递归建立左子树，假设递归返回时当前位置在j，则从j位置再递归建立右子树，最后返回根节点。

#
# class Codec:
#     def serialize(self, root):
#         if root == None: return []
#         ans = [root.val] + self.serialize(root.left) + self.serialize(root.right)
#         return ans
#
#
#     def deserialize(self, data):
#         def solve(data, i):
#             if i >= len(data) or data[i] == None:
#                 return (None, i + 1)
#             root = TreeNode(data[i])
#             lchild, k = solve(data, i + 1)
#             rchild, j = solve(data, k)
#             root.left, root.right = lchild, rchild
#             return (root, j)
#
#         return solve(data, 0)[0]


# Definition for a binary tree node.
# class TreeNode(object):
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Codec:
    """将树序列化和反序列化"""

    def __init__(self):
        self.res = []

    def serialize(self, root):
        """Encodes a tree to a single string.
            前序遍历，得到序列
        """
        if root is None:
            self.res.append(None)
            return
        self.res.append(root.val)
        self.serialize(root.left)
        self.serialize(root.right)
        return self.res

    def deserialize(self, s):

        if s is None: return  # 当数组s是空时，重构的树也是none，

        num = s.pop(0)
        if num is not None:   #防止pop from 空列表报错
            root = TreeNode(num)
            root.left = self.deserialize(s)
            root.right = self.deserialize(s)
        else:
            return None

        return root  # 每次返回的root，是上一层root的left,或者right。最后一次return树的根节点


