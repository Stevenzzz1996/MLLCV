#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 16:35

# 思路1：
# 首先将根节点的左子树变成链表
# 其次将根节点的右子树变成链表
# 最后将变成链表的右子树放在变成链表的左子树的最右边
# 思 路2
# 先序遍历中的前一个节点需要在右节点中连接先序遍历中的下一个节点，而左节点需要置空
# 利用栈实现的前序遍历。
# 把当前节点的左右子树压入栈之后，修改当前的节点左右子树，左子树赋值为空，右子树赋值为当前栈顶节点。
# 对前序遍历增加一点代码即可，简单易懂
# 思路2
class Solution:
    def flatten(self, root: TreeNode) -> None:
        if not root: return
        stack = [root]
        while stack:
            node = stack.pop()
            if node.right:
                stack.append(node.right)
            if node.left:
                stack.append(node.left)
            if stack:  # 如果有左右子树就执行左制空，右子树添加完递归弹出
                node.left =None
                node.right = stack[-1]
