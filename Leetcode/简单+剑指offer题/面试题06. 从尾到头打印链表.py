#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/30 13:26


class LinkedList:
    def __init__(self):
        self.headval = None
class ListNode:
    '''
    data: 节点保存的数据
    _next: 保存下一个节点对象
    '''
    def __init__(self, data, pnext=None):
        self.data = data
        self._next = pnext

    def reversePrint(self, head):
        stack = []
        cur = head
        while cur:
            stack.append(cur.val)
            cur = cur.next
        return stack[::-1]

    ''' 
res = []
self.helper(head, res)
return res
def helper(self, node, res):
    if node is None: return
    # 应该先判断下一个结点是否为空，如果不为空，则递归调用，在回溯的时候，才添加到结果中
    if node.next:
        self.helper(node.next, res)
    # 回溯时添加
    res.append(node.val)
            '''

if __name__ == '__main__':

    head = ListNode(1,3,2)
    print(reversePrint(head))