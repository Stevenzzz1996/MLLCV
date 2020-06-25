#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/2 16:01


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
print(singleNumbers(nums = [3,4,3,3]))

'''
        s1 = sum(nums)
        s2 = sum(list(set(nums)))*3
        return int(abs(s1-s2)/2)

        counter = collections.Counter(nums)
        return counter.most_common()[-1][0]

        nums.sort()
        if nums[0] != nums[1]: 
            return nums[0]
        for i in range(1,len(nums)-1):
            if(nums[i] != nums[i+1] and nums[i] != nums[i-1]):
                return nums[i]
        return nums[-1]
        '''