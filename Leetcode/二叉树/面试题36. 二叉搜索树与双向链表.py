#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 22:25


class Solution:
    def treeToDoublyList(self, root: 'Node') -> 'Node':
        # 二叉搜索树的中序遍历序列就是排序的数列,之后只需要把当前节点的右子树设为下一个节点,
        # 下一个节点的左子树设为该节点.
        if not root: return
        self.mid = []
        self.middle(root)
        for i in range(len(self.mid)-1):
            self.mid[i].right = self.mid[i+1]
            self.mid[i+1].left = self.mid[i]
        return self.mid[0]
    def middle(self, root):
        if not root: return
        self.middle(root.left)
        self.mid.append(root)
        self.middle(root.right)