#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/29 13:22


from typing import List
from collections import defaultdict
from collections import deque
def findLadders(beginWord: str, endWord: str, wordList: List[str]) -> List[List[str]]:
    wordList.append(beginWord)
    ### 构建具有邻接关系的桶
    buckets = defaultdict(list)
    for word in wordList:
        for i in range(len(beginWord)):
            match = word[:i] + '*' + word[i+1:]
            buckets[match].append(word)
    ##### BFS遍历
    pres = defaultdict(list)#前溯节点
    toSeen = deque([(beginWord, 1)])#待遍历列表及当前深度
    befound = {beginWord:1}#已探测到的词列表
    while toSeen:
        cur, level = toSeen.popleft()
        for i in range(len(beginWord)):
            match = word[:i] + '*' + word[i+1:]
            for word in buckets[match]:
                if word not in befound:
                    befound[word] = level+1
                    toSeen.append((word, level+1))
                if befound[word] == level+1:  #当前深度等于该词的首次遍历深度，则仍应加入前溯词列表
                    pres[word].append(cur)
        if endWord in befound and level+1 > befound[endWord]:  #已搜索到目标词，且完成当前层遍历
            break
    #### 列表推导式输出结果
    if endWord in befound:
        res = [[endWord]]
        while res[0][0] != beginWord:
            res = [[word] + r for r in res for word in pres[r[0]]]
        return res
    else:
        return []
beginWord = "hit"
endWord = "cog"
wordList = ["hot","dot","dog","lot","log","cog"]

a=findLadders(beginWord,endWord,wordList)
print(a)