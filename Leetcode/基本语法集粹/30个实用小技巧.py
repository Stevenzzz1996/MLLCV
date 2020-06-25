#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/6 11:01


# 变位词（相同字母异序词）
from collections import Counter


def anagram(first, second):
    return Counter(first) == Counter(second)


anagram("abcd3", "3acdb")  # True

# 检查内存
import sys 
variable = 30 
print(sys.getsizeof(variable))  # 24

#字节大小
def byte_size(string):
    return len(string.encode('utf-8'))


byte_size('?')  # 4

byte_size('Hello World')  # 11


#打印N次字符串
n = 2
s = "Programming"
print(s * n)  # ProgrammingProgramming

#首字母大写
s = "programming is awesome"
print(s.title())  # Programming Is Awesome

#列表细分
def chunk(list, size):
    return [list[i:i + size] for i in range(0, len(list), size)]

#压缩，以下代码使用filter（）从，将错误值（False、None、0和“ ”）从列表中删除。

def compact(lst):
    return list(filter(bool, lst))
compact([0, 1, False, 2, '', 3, 'a', 's', 34])  # [ 1, 2, 3, 'a', 's', 34 ]

# 计数
array = [['a', 'b'], ['c', 'd'], ['e', 'f']]

transposed = zip(*array)

print(transposed)  # [('a', 'c', 'e'), ('b', 'd', 'f')]

# 原因计数
import re
def count_vowels(str):
    return len(len(re.findall(r'[aeiou]', str, re.IGNORECASE))
count_vowels('foobar')  # 3
count_vowels('gym')  # 0

#首字母小写


def decapitalize(string):
    return str[:1].lower() + str[1:]

decapitalize('FooBar')  # 'fooBar'

decapitalize('FooBar')  # 'fooBar'

#将两个字库变为字典
def to_dictionary(keys, values):
    return dict(zip(keys, values))

keys = ["a", "b", "c"]    

values = [2, 3, 4]

print(to_dictionary(keys, values))  # {'a': 2, 'c': 4, 'b': 3}

#简易计算器
import operator

action = {
"+": operator.add,
"-": operator.sub,
"/": operator.truediv,
"*": operator.mul,
"**": pow
}
print(action['-'](50, 25))  # 25


#随机排序，洗牌
from copy import deepcopy

from random import randint


def shuffle(lst):
    temp_lst = deepcopy(lst)
    m = len(temp_lst)
    while (m):
    m -= 1
    i = randint(0, m)
    temp_lst[m], temp_lst[i] = temp_lst[i], temp_lst[m]
    return temp_lst

foo = [1, 2, 3]

shuffle(foo)  # [2,3,1] , foo = [1,2,3]

#获取丢失部分的默认值
d = {'a': 1, 'b': 2}
print(d.get('c', 3))  # 3

#reduce
def add(x, y) :            # 两数相加
    return x + y
reduce(add, [1,2,3,4,5])   # 计算列表和：1+2+3+4+5
15
reduce(lambda x, y: x+y, [1,2,3,4,5])  # 使用 lambda 匿名函数
15