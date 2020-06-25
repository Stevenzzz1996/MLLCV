#!usr/bin/env python
# -*- coding:utf-8 -*-
# author: sfhong2020 time:2020/3/28


"""
堆排序是一个效率要高得多的选择排序，首先把整个数组变成一个最大堆，然后每次从堆顶取出最大的元素，
这样依次取出的最大元素就形成了一个排序的数组。堆排序的核心分成两个部分，第一个是新建一个堆，第二个是弹出堆顶元素后重建堆。
新建堆不需要额外的空间，而是使用原来的数组，一个数组在另一个维度上可以当作一个完全二叉树（
除了最后一层之外其他的每一层都被完全填充，并且所有的节点都向左对齐），对于下标为i的元素，
他的子节点是2*i+1和2*i+2（前提是没有超出边界）。在新建堆的时候从左向右开始遍历，当遍历到一个元素的时候，
重新排列从这个元素节点到根节点的所有元素，保证满足最大堆的要求（父节点比子节点要大）。遍历完整个数组的时候，这个最大堆就完成了。
在弹出根节点之后（把根节点的元素和树的最底层最右侧的元素互换），堆被破坏，需要重建。
从根节点开始和两个子节点比较，如果父节点比最大的子节点小，那么就互换父节点和最大的子节点，
然后把互换后在子节点位置的父节点当作新的父节点，和它的子节点比较，如此往复直到最后一层，这样最大堆就重建完毕了。

"""


def heapify(arr, n, i):
    largest = i
    l = 2 * i + 1  # left = 2*i + 1
    r = 2 * i + 2  # right = 2*i + 2

    if l < n and arr[i] < arr[l]:
        largest = l

    if r < n and arr[largest] < arr[r]:
        largest = r

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]  # 交换

        heapify(arr, n, largest)

def heapSort(arr):
    n = len(arr)

    # Build a maxheap.
    for i in range(n, -1, -1):
        heapify(arr, n, i)

        # 一个个交换元素
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]  # 交换
        heapify(arr, i, 0)

nums = [2,8,7,1,3,5,6,4]
heapSort(nums)
print(nums)