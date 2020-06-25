#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/5 16:37


# 求所有子数组的和的最大值。
class Solution:
    def maxSubArray(self, nums) -> int:
        if not nums: return 0
        max_num = nums[0]
        for i in range(1, len(nums)):
            if nums[i-1] > 0:  # 上一个如果大于0，就加进来！原地更新！
                nums[i] += nums[i-1]
            max_num = max(max_num, nums[i])  # 实时存储最大值！
        return max_num


if __name__ == '__main__':
    print(Solution().maxSubArray(nums = [-2,1,-3,4,-1,2,1,-5,4]))
