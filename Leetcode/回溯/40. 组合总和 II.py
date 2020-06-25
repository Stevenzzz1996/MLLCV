#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/26 17:48


class Solution:
    def combinationSum2( candidates, target):
        if not candidates:
            return []
        candidates.sort()
        n = len(candidates)
        res = []

        def backtrack(i, tmp_sum, tmp):
            if tmp_sum == target:
                res.append(tmp)
                return
            for j in range(i, n):
                if tmp_sum + candidates[j] > target: break  # 和return一样的意思！
                if j > i and candidates[j] == candidates[j - 1]: continue
                backtrack(j + 1, tmp_sum + candidates[j], tmp + [candidates[j]])

        backtrack(0, 0, [])
        return res


candidates = [10, 1, 2, 7, 6, 1, 5]
target = 8
print(Solution.combinationSum2(candidates, target))
# class Solution:
#     def combinationSum2(self, candidates: List[int], target: int) -> List[List[int]]:
#         if not candidates:
#             return []
#         candidates.sort()
#         res=[]
#         n=len(candidates)

#         def helper(i,tmp,target):
#             if target==0:
#                 res.append(tmp)
#                 return
#             if i==n or target<candidates[i]:
#                 return
#             for j in range(i,n):
#                 if j>i and candidates[j]==candidates[j-1]:
#                     continue
#                 helper(j+1,tmp+[candidates[j]],target-candidates[j])
#         helper(0,[],target)
#         return res
