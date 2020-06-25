#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 16:12


class MinStack:

    def __init__(self):
        """
        initialize your data structure here.
        """
        self.A=[]
        self.B=[]
    def push(self, x: int) -> None:
        self.A.append(x)
        if not self.B or x<=self.B[-1]:
            self.B.append(x)
    def pop(self) -> None:
        if self.A.pop() == self.B[-1]:
            self.B.pop()
    def top(self) -> int:
        return self.A[-1]

    def min(self) -> int:
        if self.B:
            return self.B[-1]


# Your MinStack object will be instantiated and called as such:
# obj = MinStack()
# obj.push(x)
# obj.pop()
# param_3 = obj.top()
# param_4 = obj.min()