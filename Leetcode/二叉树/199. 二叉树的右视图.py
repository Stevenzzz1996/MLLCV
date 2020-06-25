#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/7 19:49


class Solution:
    def rightSideView(self, root: TreeNode) -> List[int]:
        def dfs(root, res, depth):
            if not root: return
            if len(res) == depth:
                res.append(root.val)
            dfs(root.right, res, depth+1)  # 执行完毕再下一个dfs！参考官方题解视频！
            dfs(root.left, res, depth+1)  # 从最开始开始！
        res = []
        dfs(root, res, 0)
        return res