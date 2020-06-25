#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 19:51


class MaxQueue:

    def __init__(self):
        self.queue = []
        self.deque = []
    def max_value(self) -> int:
        return self.deque[0] if self.deque else -1

    def push_back(self, value: int) -> None:
        self.queue.append(value)
        while  self.deque and value>self.deque[-1]:
            self.deque.pop(-1)
        self.deque.append(value)

    def pop_front(self) -> int:
         #数据队列元素为最大值时才出栈单调栈元素
        front = self.queue and self.queue.pop(0)
        if self.deque and self.deque[0] == front:
            self.deque.pop(0)
        return front or -1