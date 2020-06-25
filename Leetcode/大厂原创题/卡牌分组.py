#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong 2020 time:2020/3/28

from collections import Counter

def hasGroupsSizeX(deck):
    count = Counter(deck)
    n = len(deck)
    for i in range(2, n + 1):
        if n % i == 0:
            if all(val % i == 0 for val in count.values()):
                return True
    return False
deck = list(map(int,input().split()))

print(hasGroupsSizeX(deck))