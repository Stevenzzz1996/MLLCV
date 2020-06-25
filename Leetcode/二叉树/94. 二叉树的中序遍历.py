#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 14:21


class Solution:
    def inorderTraversal(self, root: TreeNode) -> List[int]:
        res = []
        stack = []
        # 用p当做指针
        p = root
        while p or stack:
            # 把左子树压入栈中
            while p:
                stack.append(p)
                p = p.left
            # 输出 栈顶元素
            p = stack.pop()
            res.append(p.val)
            # 看右子树
            p = p.right
        return res
# class Solution:
#     def inorderTraversal(self, root: 'TreeNode', p: 'TreeNode') -> 'TreeNode':
#         def inorder(node):
#             if not node:return
#             return inorder(node.left) + [node] + inorder(node.right)

class Solution:
    def inorderTraversal(self, root: TreeNode) -> List[int]:
        res = []
        def helper(root):
            if not root:
                return
            helper(root.left)
            res.append(root.val)
            helper(root.right)
        helper(root)
        return res

