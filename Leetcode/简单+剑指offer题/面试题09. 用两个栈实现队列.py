#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/30 15:36


class CQueue:

    def __init__(self):
        self.A = []
        self.B = []

    def appendTail(self, value: int) -> None:
        self.A.append(value)

    def deleteHesd(self) -> int:
        #首先考虑都为空
        if not self.A and not self.B: return -1
        #其次B为空
        if not self.B:
             # 当A一直有时，一直转到B中，直到A为空
             while self.A:
                self.B.append(self.A.pop())
                return self.B.pop()
        #最后B不为空，直接取
        return self.B.pop()
