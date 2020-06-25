#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/30 20:26


def movingCount(m, n, k):
    if k < 0 or m == 0 or n == 0: return 0
    marked = [0 for _ in range(n * m)]

    def dfs(x, y, marked, k, m, n):
        index = x*n+y
        cnt = 0
        if 0 <= x < m and 0 <= y < n and (sum(map(int, str(x))) + sum(map(int, str(y)))) <= k and not marked[index]:
            marked[index] = 1
            cnt=1+dfs(x+1,y,marked,k,m,n) + dfs(x-1,y,marked,k,m,n) \
                + dfs(x,y+1,marked,k,m,n) + dfs(x,y-1,marked,k,m,n)
        return cnt

    cnt = dfs(0, 0, marked, k, m, n)
    return cnt


m = 2
n = 3
k = 1
print(movingCount(m, n, k))
