#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/24 11:35


# 总的思路为遍历所有从nums1里挑出i个数与nums2里挑出k-i个数的组合方案并取最大值
#
# 子问题从nums里挑数需满足相对顺序不变的最大数
#
# 子问题合并两个数组也需满足两个数组元素的相对顺序不变的最大数
#
class Solution:
    def maxNumber(self, nums1, nums2, k):
        def pick(nums, k):  # 从nums里取出相对顺序不变的k个数构成的最大数
            if not k:
                return []
            res, _pop = [], len(nums) - k  # _pop为允许pop的个数
            while nums:
                num = nums.pop(0)
                while _pop and res and res[-1] < num:
                    _pop -= 1
                    res.pop()
                res.append(num)
            return res[:k]

        def merge(nums1, nums2):  # 将nums1和nums2各自元素的相对顺序不变合并能产生的最大数
            res = []
            while nums1 and nums2:
                res.append(nums1.pop(0)) if nums1 > nums2 else res.append(nums2.pop(0))
            res.extend(nums1 or nums2)
            return res

        _max = []
        for i in range(k + 1):  # 遍历所有组合方式，取最大的结果
            if i <= len(nums1) and k - i <= len(nums2):
                _max = max(_max, merge(pick(nums1.copy(), i), pick(nums2.copy(), k - i)))
        return _max

nums1 = [3, 4, 6, 5]
nums2 = [9, 1, 2, 5, 8, 3]
k = 5
if __name__ == '__main__':
    print(Solution().maxNumber(nums1,nums2,k))























