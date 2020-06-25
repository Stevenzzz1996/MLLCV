#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/30 19:20


def existWordWay(board, word):
    m, n = len(board), len(board[0])
    if m == 0: return False
    marked = [[False for _ in range(n)] for _ in range(m)]
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    def search_word(board, word, index, x, y, marked, m, n):
        # 特判，终止条件！不用会报错！字符串 word 已全部匹配，即 index = len(word) - 1
        if index == len(word) - 1:
            return board[x][y] == word[index]  # 直接返回True也可以！

        if word[index] == board[x][y]:
            marked[x][y] = True  # 走过的地方标为对，继续向外探索，
            for d in directions:
                newx, newy =  x + d[0], y + d[1]   # not False 代表不能返回去搜索
                if 0 <= newx < m and 0 <= newy < n and not marked[newx][newy] and \
                    search_word(board, word, index+1, newx, newy, marked, m, n):   # 下一个继续找直到全部匹配到为止，然后回溯回去
                    return True
            marked[x][y] = False

    for i in range(m):
        for j in range(n):
            if search_word(board, word, 0, i, j, marked, m, n):
                return True   #有一个往下深入搜索全部匹配到了回溯回来，就返回True
        return False




board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]
word = "ABCCED"
print(existWordWay(board,word))

# class Solution:
#     def exist(self, board: List[List[str]], word: str) -> bool:
#         def dfs(i, j, k):
#             if not 0 <= i < len(board) or not 0 <= j < len(board[0]) or board[i][j] != word[k]: return False
#             if k == len(word) - 1: return True
#             tmp, board[i][j] = board[i][j], '/'
#             res = dfs(i + 1, j, k + 1) or dfs(i - 1, j, k + 1) or dfs(i, j + 1, k + 1) or dfs(i, j - 1, k + 1)
#             board[i][j] = tmp
#             return res
#
#         for i in range(len(board)):
#             for j in range(len(board[0])):
#                 if dfs(i, j, 0): return True
#         return False

