#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/5 21:01


class Solution:
    def nthUglyNumber(self, n: int) -> int:
        import heapq
        heap = [1]
        heapq.heapify(heap)  # 默认是小顶堆！顶部是最小值
        res = 0
        for _ in range(n):
            res = heapq.heappop(heap)  # 取就完事了！
            while heap and res == heap[0]:  # 防止有多个丑数出现，比如2*3==3*2，丑数只有一个！
                res = heapq.heappop(heap)
            a, b, c = res * 2, res * 3, res * 5
            for t in [a, b, c]:
                heapq.heappush(heap, t)  # 一直堆进去
        return res

if __name__ == '__main__':
    print(Solution().nthUglyNumber(10))

# 最小栈也能实现！
# class Solution:
#     def nthUglyNumber(self, n: int) -> int:
#         c = set()
#         m = 1
#         stack = [1]
#         d = []
#         while len(d) < n:
#             m = min(stack)
#             stack.remove(m)
#             d.append(m)
#             if m * 2 not in c:
#                 stack.append(m * 2)
#                 c.add(m * 2)
#             if m * 3 not in c:
#                 stack.append(m * 3)
#                 c.add(m * 3)
#             if m * 5 not in c:
#                 stack.append(m * 5)
#                 c.add(m * 5)
#         return d[- 1]