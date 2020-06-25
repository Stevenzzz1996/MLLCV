#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/6/3 21:14


def repeat_num(arrayA: list) -> int:
    dup ={}
    for index, value in enumerate(arrayA):
        if value != index:  # 如果当前元素和当前元素的下标不相同
            if value == arrayA[value]:  # 如果当前元素和当前元素作为下标的元素存在，说明重复
                 dup[index]=value
            else:
                 arrayA[index], arrayA[value] = arrayA[value], arrayA[index]  # 互换之后，当前元素作为下标的元素和当前元素一致。
    return dup
if __name__ == '__main__':
    d = repeat_num([1,2,3,4,4,5,6,5,2,2,3,7,7,5])
    print(d)