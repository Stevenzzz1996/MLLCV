#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/30 14:18


class Solution:
    def getPermutation(self, n: int, k: int) -> str:
        def fact(n):
            res = 1
            while n:
                res *= n
                n -= 1
            return res
        def dfs(tmp, path, k):
            if not tmp:
                return path
            n = len(tmp)
            count = fact(n-1)  # 对于每一层，该层每个分支的数量相当于剩余数量-1的阶乘
            for i in range(n):
                if k > count:  # 此处如果k大于该分支排列数量，那么减去该分支
                    k -= count
                else:
                    return dfs(tmp[:i]+tmp[i+1:], path+tmp[i], k)
        return dfs([str(i) for i in range(1, n+1)], '', k)

if __name__ == '__main__':
    n = 3
    k=3
    print(Solution().getPermutation(n,k))
