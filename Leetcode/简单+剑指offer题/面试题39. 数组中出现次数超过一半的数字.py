#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/1 10:50


from collections import Counter
def majorityElement(nums):
    # count = Counter(nums)
    # return count.most_common(1)[0][0]  # 第一多的数字，然后返回第一个里面的第一个（key）：比如2最多有4个，返回2

    # dic = collections.Counter(nums)
    #         for key,value in dic.items():
    #             if value > len(nums) / 2:
    #                 return key

    res = []  # 或者写成None!
    cnt = 0
    for num in nums:  # 留下数组中出现次数最高的数
        if not res:
            res = num
            cnt = 1
        else:
            if num == res:
                cnt += 1
            else:
                cnt -= 1
                if cnt == 0:
                    res = []
    # 判断次数是否大于一半
    cnt = 0
    for i in nums:
        if num == res:
            cnt += 1
    if cnt > len(nums) / 2:
        return res
    else:
        return 0
print(majorityElement([1, 2, 3, 2, 2, 2, 5, 4, 2]))