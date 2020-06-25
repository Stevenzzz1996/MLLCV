#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/15 11:17


T = int(input())
nums = []
for i in range(T):
    K = [int(i) for i in input().split()]
    for j in range(len(K)):
        nums.append(K[j])
nums.sort()
print(nums)
# class Node:
#     def __init__(self, elem, next_=None):
#         self.elem = elem
#         self.next = next_
# def list2link(List):
#     head = Node(List[0])#创建一个头节点并将list第一个值赋值给头结点
#     p = head#创建头指针
#     for i in range(1, len(List)):#list从第二位开始遍历
#         p.next = Node(List[i])#下一个结点p.next指向list值
#         p = p.next #指针往下移动
#     return head #返回头结点
#
# if __name__ == "__main__":
#     old_list = nums
#     link = list2link(old_list)
#     print(link)

# 10000010输出描述：
# 输出为一个数字，表示在原本的土地状态下，还可种下的最大花草数量。假如用一个数列表示土地上的种植情况（数列元素仅由0、1组成，1表示该区域已种植，0则表示未种植）。现在请你帮助园艺工作人员，
# 在不影响原有花草的情况下，计算出可新种植的最大花草数量。
#
# 保存成链表!