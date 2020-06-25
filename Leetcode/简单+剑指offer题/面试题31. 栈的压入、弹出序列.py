#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 17:24


# 重点是模拟入栈出栈，定义一个stack模拟入栈和出栈，如果stack[-1] == poped的第一个元素，就开始出栈直到空！
def validateStackSequences(pushed, poped):
    j = 0
    stack = []
    for i in pushed:
        stack.append(i)
        while stack and j < len(poped) and stack[-1] == poped[j]:
            stack.pop()
            j += 1
    return j == len(poped)


print(validateStackSequences(pushed = [1,2,3,4,5], poped = [4,5,3,2,1]))