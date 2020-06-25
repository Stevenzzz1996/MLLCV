#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 21:38


# 输入：[1,7,5,1,9,2,5,1]
# 输出：[7,9,9,9,0,5,0,0]


class Solution:
    def nextLargerNodes(self, head: ListNode) -> List[int]:
        nums = []
        node = head
        while node:
            nums.append(node.val)
            node = node.next

        stack = []
        stack_loc = []
        res = [0] * len(nums)

        for i in range(len(nums)):
            while stack and stack[-1] < nums[i]:
                res[stack_loc[-1]] = nums[i]
                stack.pop()
                stack_loc.pop()
            stack.append(nums[i])
            stack_loc.append(i)

        return res
import numpy as np

print(np.random.random((10,2)))