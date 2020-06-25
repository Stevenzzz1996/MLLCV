#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/26 15:08


# def combinationSum(candidates,target):
#     candidates.sort()
#     n = len(candidates)
#     res = []
#
#     def helper(i, tmp_sum, tmp):
#         if tmp_sum > target or i == n:
#             return
#         if tmp_sum == target:
#             res.append(tmp)
#             return
#         helper(i, tmp_sum + candidates[i], tmp + [candidates[i]])
#         helper(i + 1, tmp_sum, tmp)
#
#     helper(0, 0, [])
#     return res

class Solution(object):
    def combinationSum(candidates, target):
        if not candidates: return
        if min(candidates) > target: return
        candidates.sort()
        res = []

        def helper(candidates, target, tmp):
            if target == 0:
                res.append(tmp)
            if target < 0:
                return
            for i in range(len(candidates)):
                if candidates[i] > target:
                    break
                helper(candidates[i:], target - candidates[i], tmp + [candidates[i]])
        helper(candidates, target, [])
        return res

candidates = [2,3,6,7]
target = 7
print(Solution.combinationSum(candidates, target))