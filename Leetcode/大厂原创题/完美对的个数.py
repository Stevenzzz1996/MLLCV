#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/4/26 22:45

# a题目描述
# 有n个物品，每个物品有k个属性，第i件物品的第j个属性用一个正整数表示记为ai，两个不同的物品ij，被认为是完美对的当且仅当 ai1+aj1=ai2+aj2=…=ai,k+aj,k
# ，求完美对的个数。
# 输入描述：
# 第一行两个数n，k。j
# |接下来n行，第1行k个数字表示ai，1，ai，2，…，ai，k
# |1sn≤105，2sk≤10，1sai≤100输出描述：
# 一行一个数字表示答案
# 示例1输入输出示例仅供调试，后台判题数据一般不包含示例输入
# 5 3
# 2 11 21
# 19 10 1
# 20 11 1
# 6 15 24
# 18 27 36
# 输出3