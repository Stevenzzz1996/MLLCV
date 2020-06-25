#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 13:20


# 输入两棵二叉树A和B，判断B是不是A的子结构。(约定空树不是任意一个树的子结构)
#
# B是A的子结构， 即 A中有出现和B相同的结构和节点值。
def isSubStructure(A, B):
    # 四种情况
    def helper(A, B):
        if not A:  # 如果A 往下没了，就找不到和B相同的了
            return False
        if not B:  # 如果往下没了，说明符合要求！因为B没找到不符合的
            return True
        if A.val == B.val:  # 这是要分别往下找，必须都执行，看谁能找到，而不是执行其中一个，贪心
            return helper(A.left, B.left) and helper(A.right, B.right)
        return False  # 如果A，B不相等

    # 先整体判断，也要判断整体的是否相等，没找到再继续往下找！
    if not A or not B:  # 有一个为空
        return False
    if helper(A, B):  # 子树找到了
        return True
    if A.val == B.val:  # 如果根相等, 左右分别执行，有一边匹配就对，而不用都满足，，所以用or！
        return isSubStructure(A.left, B) or isSubStructure(A.right, B)


# class Solution:
#     def isSubStructure(self, A: TreeNode, B: TreeNode) -> bool:
#         def helper(A, B):
#             if not B:
#                 return True
#             if not A:
#                 return False
#             if A.val == B.val:
#                 return helper(A.left, B.left) and helper(A.right, B.right)
#             return False
#
#         if not A or not B:
#             return False
#         if helper(A, B):
#             return True
#         return self.isSubStructure(A.left, B) or self.isSubStructure(A.right, B)