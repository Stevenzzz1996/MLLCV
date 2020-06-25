#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/5 15:02


# 请设计一个函数，用来判断在一个矩阵中是否存在一条包含某字符串所有字符的路径。路径可以从矩阵中的任意一格开始，
# 每一步可以在矩阵中向左、右、上、下移动一格。如果一条路径经过了矩阵的某一格，那么该路径不能再次进入该格子。
# 例如，在下面的3×4的矩阵中包含一条字符串“bfce”的路径（路径中的字母用加粗标出）。

class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        m, n = len(board), len(board[0])
        if m == 0: return False

        marked = [[False for _ in range(n)] for _ in range(m)]
        for i in range(m):
            for j in range(n):
                if self.search_word(board, word, 0, i, j, marked, m, n):
                    return True
        return False

    directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]

    def search_word(self, board, word, index, x, y, marked, m, n):
        if index == len(word) - 1:  # word只有一个
            return board[x][y] == word[index]
        if board[x][y] == word[index]:  # 关键点！从word的第一个开始找！
            marked[x][y] = True
            for direction in self.directions:
                new_x = x + direction[0]
                new_y = y + direction[1]
                if 0 <= new_x < m and 0 <= new_y < n and not marked[new_x][new_y] and \
                        self.search_word(board, word, index + 1, new_x, new_y, marked, m, n):
                    return True
            marked[x][y] = False

        return False

matrix = [
    ["a","b","c","e"],
    ["s","f","c","s"],
    ["a","d","e","e"]
]
word = 'bfce'
