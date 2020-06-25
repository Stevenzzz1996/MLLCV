#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/31 22:27


def permutation(s):
    if not s: return
    s = list(sorted(s))
    res = []

    def helper(s, tmp):
        if not s: res.append(''.join(tmp))  # 等到为空时，将其一起拼接！
        for i, char in enumerate(s):
            if i > 0 and s[i] == s[i - 1]:   # 防止元素重复！
                continue
            helper(s[:i] + s[i + 1:], tmp + [char])  # 去除了i 继续往下遍历，i对应的加入到tmp中！

    helper(s, [])
    return res
print(permutation("abc"))