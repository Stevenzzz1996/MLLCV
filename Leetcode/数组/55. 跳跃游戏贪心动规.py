#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/30 10:54


# 们依次遍历数组中的每一个位置，并实时维护 最远可以到达的位置。
# 对于当前遍历到的位置 xx，如果它在 最远可以到达的位置 的范围内，
# 那么我们就可以从起点通过若干次跳跃到达该位置，因此我们可以用i+nums[i] 更新 最远可以到达的位置。
# 正向 贪心！
class Solution:
    def canJump(self, nums: List[int]) -> bool:
        if 0 not in nums: return True  # 如果没有0则一定可以到达
        if len(nums) < 2: return True
        max_distance = nums[0]  # 设定可以达到的最大坐标
        for i in range(1, len(nums) - 1):
            if i <= max_distance:  # 表示当前坐标可以达到
                max_distance = max(max_distance, i + nums[i])  # 更新可以达到的最远坐标
        return max_distance >= len(nums) - 1

# 正向 贪心！
def canjump(nums):
    n = len(nums)
    right = 0
    if len(nums) == 1:
        return True
    if len(nums) == 0 or nums[0] == 0:
        return False
    for i in range(n):
        if i <= right:
            right = max(i+nums[i],right)
            if right >= n-1:  # 与索引进行比较！
                return True
    return False
print(canjump([2,3,1,1,4]))
print(canjump([3,2,1,0,4]))
# 逆向
class Solution:
    def canJump(self, nums: List[int]) -> bool:
        right = len(nums)-1
        for i in range(len(nums)-2,-1,-1):
            if nums[i] >= right-i:
                right = i
        if right==0:  # 【0】放出来
            return True
        return False


# 动规
class Solution(object):
    def canJump(self, nums):
        if len(nums) == 1: return True
        if len(nums) == 0: return False
        dp = [0] * len(nums)
        dp[0] = nums[0]
        for i in range(1,len(nums)):
            if i > dp[i-1]:
                return False  # 第i个走不到
            else:
                dp[i] = max(dp[i-1], i + nums[i])
                if dp[i] >= len(nums) - 1:
                    return True
        return False

# BFS
class Solution(object):
    def canJump(self, nums):
        if len(nums) == 1:
            return True
        if len(nums) == 0:
            return False
        q = deque()
        visited = set()
        visited.add(0)
        q.append(0)
        while q:
            idx = q.pop()
            if idx >= len(nums)-1 or nums[idx] + idx >= len(nums) - 1:
                return True
            if idx >= 0 and nums[idx] == 0 or idx+nums[idx] in visited:
                idx -= 1
                while idx in visited:
                    idx -= 1
                    continue
                if idx == -1:return False
                else:
                    q.append(idx)
                    visited.add(idx)
            else:
                q.append(idx + nums[idx])
                visited.add(idx + nums[idx])
        return False


