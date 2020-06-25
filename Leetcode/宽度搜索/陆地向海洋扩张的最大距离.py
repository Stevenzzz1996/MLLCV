#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/29 10:28


"""力扣1126 地图分析
此题是一个标准的广度优先题目。
基本思路就是不断模拟从陆地向海洋扩张的最长距离：

查找初始所有陆地坐标，并进行判断是否为空或长度与grid大小一致，满足条件即输出-1
定义一个判断给定坐标值是否有效的辅助函数：isValid(x, y)
定义一个4向delt列表，用于从当前坐标生成新坐标，并初始化depth=-1
从当前陆地坐标列表开始向外扩张探索：
对于每个待搜索的陆地坐标，依次生成4个方向新的坐标值
    若新坐标值尚未探索到，则加入到待探索列表tmp，并将其"填充"为陆地(即赋值为1)，避免重复探索
    若当前深度所有陆地周边仍有待探索的海洋（即tmp不为空），则继续探测
最后，需特殊考虑depth初值问题：由于陆地初始值是已有深度，当其探索一层后方可赋值为1，所以其初始值实际上应为-1.
"""

def maxDistance(grid) -> int:
    m, n = len(grid), len(grid[0])
    nodes = [(i, j) for i in range(m) for j in range(n) if grid[i][j]]  #提取陆地坐标列表
    if not nodes or len(nodes) == m * n:  # 是否为纯陆地或纯海洋
        return -1
    def isValid(x, y):   # 判断给定坐标是否有效
        return 0 <= x < m and 0 <= y < n

    depth = -1
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while nodes:  #处理当前层信息
        depth += 1
        ocean = []  # 存储待探索海洋坐标
        for x, y in nodes:
            for d in directions:
                newx, newy = x+d[0], y+d[1]
                if isValid(newx, newy) and not grid[newx][newy]:  #新点是海洋且未探测
                    ocean.append((newx, newy))
                    grid[newx][newy] = 1
        nodes = ocean

    return depth
grid=[[1,0,0],[0,0,0],[0,0,0]]
print(maxDistance(grid))
