#!usr/bin/env python
# -*- coding:utf-8 -*-
# author:  xinlan time:2020/3/28

colors = ['red', 'blue', 'red', 'green', 'blue', 'blue']
res = {}
for color in colors:
    if res.get(color) == None:
        res[color]=1
    else:
        res[color]+=1
print(res)

from collections import Counter
c=Counter(colors)

c=c.most_common(2)
print(c)
"""
from collections import defaultdict
#dict[element] = xxx,但前提是element字典里，如果不在字典里就会报错

dict1 = defaultdict(int)
dict2 = defaultdict(set)
dict3 = defaultdict(str)
dict4 = defaultdict(list)
dict1[2] ='two'

print(dict1[1])
print(dict2[1])
print(dict3[1])
print(dict4[1])

# 0
# set()
# 
# []
"""