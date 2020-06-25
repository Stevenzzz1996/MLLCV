#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/29 11:27

"""
对给定的 wordList 做预处理，找出所有的通用状态。将通用状态记录在字典中，
键是通用状态，值是所有具有通用状态的单词。
将包含 beginWord 和 1 的元组放入队列中，1 代表节点的层次。
我们需要返回 endWord 的层次也就是从 beginWord 出发的最短距离。
为了防止出现环，使用访问数组记录。
当队列中有元素的时候，取出第一个元素，记为 current_word。
找到 current_word 的所有通用状态，并检查这些通用状态是否存在其它单词的映射，
这一步通过检查 all_combo_dict 来实现。
从 all_combo_dict 获得的所有单词，都和 current_word 共有一个通用状态，
所以都和 current_word 相连，因此将他们加入到队列中。
对于新获得的所有单词，向队列中加入元素 (word, level + 1) 其中 level 是 current_word 的层次。
最终当你到达期望的单词，对应的层次就是最短变换序列的长度。
"""
from collections import defaultdict
def ladderLength(beginword, endword, wordlist):
    #特判
    if not endword or not beginword or not wordList or endword not in wordlist:
        return 0
    n = len(beginword)  #所有单词长度一样
    combine_dict = defaultdict(list)  #创建字典
    for word in wordlist:
        for i in range(n):
            combine_dict[word[:i] + "*" + word[i+1:]].append(word)  #键值对键是带*，值是原来的单词
    #Key是通用词
    # Value是具有相同中间泛型单词的单词列表。
    queue = [(beginword, 1)]
    visited = {beginword: True}
    while queue:
        cur_word, level = queue.pop(0)
        for i in range(n):
            #当前单词的中间词
            intermediate_word = cur_word[:i] + "*" + cur_word[i + 1:]

            for word in combine_dict[intermediate_word]:
                if word == endword:
                    return level + 1
                if word not in visited:
                    visited[word] = True
                    queue.append((word, level+1))
            combine_dict[intermediate_word] = []
    return 0

beginWord = "hit"
endWord = "cog"
wordList = ["hot","dot","dog","lot","log","cog"]

a=ladderLength(beginWord,endWord,wordList)
print(a)