#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/25 10:39


# 方法：排序 + 最长递增子序列
# 该问题为最长递增子序列的二维问题。
#
# 我们要找到最长的序列，且满足 seq[i+1] 中的元素大于 seq[i] 中的元素。
#
# 该问题是输入是按任意顺序排列的——我们不能直接套用标准的 LIS 算法，需要先对数据进行排序。我们如何对数据进行排序，以便我们的 LIS 算法总能找到最佳答案？
#
# 我们可以在这里找到最长递增子序列的解决方法。如果您不熟悉该算法，请先理解该算法，因为它是解决此问题的前提条件。
#
# 算法：
# 假设我们知道了信封套娃顺序，那么从里向外的顺序必须是按 w 升序排序的子序列。
#
# 在对信封按 w 进行排序以后，我们可以找到 h 上最长递增子序列的长度。
#
# 我们考虑输入 [[1，3]，[1，4]，[1，5]，[2，3]]，如果我们直接对 h 进行 LIS 算法，我们将会得到 [3，4，5]，显然这不是我们想要的答案，因为 w 相同的信封是不能够套娃的。
#
# 为了解决这个问题。我们可以按 w 进行升序排序，若 w 相同则按 h 降序排序。则上述输入排序后为 [[1，5]，[1，4]，[1，3]，[2，3]]，再对 h 进行 LIS 算法可以得到 [5]，长度为 1，是正确的答案。这个例子可能不明显。
#
# 我们将输入改为 [[1，5]，[1，4]，[1，2]，[2，3]]。则提取 h 为 [5，4，2，3]。我们对 h 进行 LIS 算法将得到 [2，3]，是正确的答案。

from bisect import bisect_left
class Solution:
    def maxEnvelopes(self,arr):
        # sort increasing in first dimension and decreasing on second
        arr.sort(key=lambda x: (x[0], -x[1]))

        def lis(nums):
            dp = []
            for i in range(len(nums)):
                idx = bisect_left(dp, nums[i])
                if idx == len(dp):
                    dp.append(nums[i])
                else:
                    dp[idx] = nums[i]
            return len(dp)
        # extract the second dimension and run the LIS
        return lis([i[1] for i in arr])

arr=[[1,5],[1,4],[1,2],[2,3]]
if __name__ == '__main__':
    print(Solution().maxEnvelopes(arr))

# Bisect模块提供的函数有：

# bisect.bisect_left(a,x, lo=0, hi=len(a)) :
#
# 查找在有序列表 a 中插入 x 的index。lo 和 hi 用于指定列表的区间，默认是使用整个列表。如果 x 已经存在，在其左边插入。返回值为 index。
#
# bisect.bisect_right(a,x, lo=0, hi=len(a))
# bisect.bisect(a, x,lo=0, hi=len(a)) ：
# 这2个函数和 bisect_left 类似，但如果 x 已经存在，在其右边插入。
#
# bisect.insort_left(a,x, lo=0, hi=len(a)) ：
# 在有序列表 a 中插入 x。和 a.insert(bisect.bisect_left(a,x, lo, hi), x) 的效果相同。
#
# bisect.insort_right(a,x, lo=0, hi=len(a))
#
# bisect.insort(a, x,lo=0, hi=len(a)) :

# 和 insort_left 类似，但如果 x 已经存在，在其右边插入。

# Bisect 模块提供的函数可以分两类： bisect* 只用于查找 index， 不进行实际的插入；而 insort* 则用于实际插入。