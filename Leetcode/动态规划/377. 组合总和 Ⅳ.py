#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/25 20:0


# dp[i]表示数字i可以用数组组成的个数
class Solution:
    def combinationSum4(nums, target):
        size = len(nums)
        if size == 0 or target <= 0: return 0
        dp = [0 for _ in range(target + 1)]
        # 因为 0 表示空集，空集和它"前面"的元素凑成一种解法，所以是 1
        dp[0] = 1
        for i in range(1, target + 1):
            for j in range(size):
                if i >= nums[j]:
                    dp[i] += dp[i - nums[j]]
        return dp[-1]
if __name__ == '__main__':
    print(Solution.combinationSum4([1,2,3],4))

# dp[0]=1
# dp[1] = dp[1]+dp[1-1]=1
# dp[2] = dp[2]+dp[2-1]+dp[2-2]=0+dp[2-1]+dp[2-2]=0+1+1=2
# dp[3] = dp[3]+dp[3-1]+dp[3-2]+dp[3-3]=0+dp[3-1]+dp[3-2]+dp[3-3]=0+dp[2]+dp[1]+dp[0]=4
# dp[4] = dp[4]+dp[4-1]+dp[4-2]+dp[4-3]=0+dp[4-1]+dp[4-2]+dp[4-3]=0+dp[3]++dp[2]+dp[1] = 1+2+4=7 = 前面相加！