#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/27 20:51


# 创建两个指针first和last，first初始为0，last初始为2，判断两指针位置之间是否为等差数列，
# 是就last往后移一位，否就fisrt = last -1，每增加一位数，等差数列增加量为last - first -1，遍历一遍就行了

class Solution:
    def numberOfArithmeticSlices( A) :
        if len(A) < 3:
            return 0
        else:
            first = 0
            last = 2
            res = 0
            while last < len(A):
                if A[last] - A[last-1] == A[first+1] - A[first]:
                    res += last - first -1  # 2,5,8,11中last加了1而first没有加，有三组！
                    last += 1
                else:
                    first = last-1
                    last = first+2
        return res
if __name__ == '__main__':
    print(Solution.numberOfArithmeticSlices([1, 2, 5, 8, 11]))