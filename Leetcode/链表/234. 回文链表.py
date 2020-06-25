#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/5/8 20:50


class Solution:
    def isPalindrome(self, head: ListNode) -> bool:
        res = []
        cur = head
        while cur:
            res.append(cur.val)
            cur = cur.next
        return res[:] == res[::-1]
'''
        if not (head and head.next): return True
        arr,i = [],0
        while head:
            _,head = arr.append(head.val),head.next
        j = len(arr)-1
        while i<j:
            if arr[i]!=arr[j]:
                return False
            i,j = i+1,j-1
        return True
'''