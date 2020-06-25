#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/12 16:23

#要注意的是：s.erase(i，1)之后，s的长度发生变化；且i指向元素删除后，i不需要再加1，因为后面的自动前移了，继续处理即可。
s = list('abbbaasssb')
def remove_letter(s):
    i = 0
    j = 0
    while i < len(s):
        j = i
        while j < len(s) and s[i] == s[j]:
            j += 1
        if j - i >= 3:
            s = s[:i] + s[j:]
            i -= 2
            if i < 0:
                i = 0
        else:
            i = j

    return s

print(remove_letter(s))
def elimination(s):
    l = 0
    while l < len(s):
        r = l  # 把右指针更新为当前位置
        while r < len(s) and s[r] == s[l]:
            r += 1
        if r - l >= 3:  # 如果找到三个以上重复的元素
            s = s[:l] + s[r:]  # 在s中删除
            l -= 2  # l回退2个位置,比如CCDDD, 回退两个位置能使l指向第一个C
            if l < 0:
                l = 0
        else:
            l = r
            # l += 1  # 这里也可以是l+=1，但是会存在一定的重复运算 比如CCB,l先指向第一个C,然后又要指向第二个C,但r-l都不满足>=3
    return s

s = 'abbbaasssb'
ans = elimination(s)
print(ans)
