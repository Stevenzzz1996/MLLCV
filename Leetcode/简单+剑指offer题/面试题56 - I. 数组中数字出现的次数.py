#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 14:23


def singleNumbers(nums):
    hashtable = {}
    res=[]
    for num in nums:
        if num not in hashtable:
            hashtable[num] = 1
        else:
            hashtable[num] += 1
    for num in nums:
        if hashtable[num]==1:
            res.append(num)

    return res

print(singleNumbers(nums = [4,1,4,6]))

#异或的性质
# 两个数字异或的结果a^b是将 a 和 b 的二进制每一位进行运算，得出的数字。 运算的逻辑是
# 如果同一位的数字相同则为 0，不同则为 1
# 任何数和本身异或则为0, a^a=0, 0^a=a, 0^0=0
# 任何数和 0 异或是本身

class Solution:
    def singleNumber(self, nums: List[int]) -> int:
        res = 0
        for i in range(32):
            cnt = 0  # 记录当前 bit 有多少个1
            bit = 1 << i  # 记录当前要操作的 bit
            for num in nums:
                if num & bit != 0:
                    cnt += 1
            if cnt % 3 != 0:
                # 不等于0说明唯一出现的数字在这个 bit 上是1
                res |= bit

        return res - 2 ** 32 if res > 2 ** 31 - 1 else res