#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/6 15:14

import heapq
class Solution:
    def minRefuelStops(self, target: int, startFuel: int, stations) -> int:
        pq = []  # A maxheap is simulated using negative values
        stations.append((target, float('inf')))
        tank=startFuel
        ans = prev = 0
        for location, capacity in stations:
            tank -= location - prev
            while pq and tank < 0:  # must refuel in past
                tank += -heapq.heappop(pq)
                ans += 1
            if tank < 0: return -1
            heapq.heappush(pq, -capacity)
            prev = location
        return ans
target = 100
startFuel = 10
stations = [[10,60],[20,30],[30,30],[60,40]]
if __name__ == '__main__':
    print(Solution().minRefuelStops(target,startFuel,stations))