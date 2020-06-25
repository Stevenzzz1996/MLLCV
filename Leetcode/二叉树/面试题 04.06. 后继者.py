#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 11:37


# 设计一个算法，找出二叉搜索树中指定节点的“下一个”节点（也即中序后继）。
#
# 如果指定节点没有对应的“下一个”节点，则返回null。
# 返回索引！

class Solution:
    def inorderSuccessor(self, root: 'TreeNode', p: 'TreeNode') -> 'TreeNode':
        def inorder(node):
            if not node: return
            return inorder(node.left)+[node]+inorder(node.right)
        Inorder = inorder(root)
        for i, node in enumerate(Inorder):
            if p.val == node.val:
                return Inorder[i+1] if i != len(Inorder) - 1 else None

'''   
         
class Solution1:
    def inorderSuccessor(self, root: 'TreeNode', p: 'TreeNode') -> 'TreeNode':
            if root:
                if root.val > p.val:  # p is in the left subtree of root
                    return self.inorderSuccessor(root.left, p) or root
                return self.inorderSuccessor(root.right, p)
'''