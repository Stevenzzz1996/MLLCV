#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 10:50


# 给定一个不含重复元素的整数数组。一个以此数组构建的最大二叉树定义如下：
#
# 二叉树的根是数组中的最大元素。
# 左子树是通过数组中最大值左边部分构造出的最大二叉树。
# 右子树是通过数组中最大值右边部分构造出的最大二叉树。

class Solution:
    def constructMaximumBinaryTree(self, nums: List[int]) -> TreeNode:
        if nums == []: return
        max_num = max(nums)
        max_index = nums.index(max_num)
        root = TreeNode(max_num)
        root.left = self.constructMaximumBinaryTree(nums[0:max_index])
        root.right = self.constructMaximumBinaryTree(nums[max_index+1:])
        return root