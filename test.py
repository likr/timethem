# coding: utf-8

import os
import unittest
import timethem

figpath = os.path.abspath(os.path.dirname(__file__)) + '/figs/'


@timethem.timethem([2000000, 4000000, 6000000, 8000000, 10000000],
                   number=1,
                   plotparams={'filename': figpath + 'test_sort.jpg'})
class TestSort(unittest.TestCase):
    def setUp(self, n):
        self.data = list(range(n))

    def test_sort(self):
        data = self.data[:]
        data.sort()


@timethem.timethem(range(100000, 500001, 100000), number=10,
                   plotparams={'filename': figpath + 'test_loop.jpg'})
class TestLoop(unittest.TestCase):
    def setUp(self, n):
        self.data = range(n)

    def test_loop(self):
        result = []
        for x in self.data:
            result.append(2 * x)

    def test_map(self):
        list(map(lambda x: 2 * x, self.data))

    def test_list_comprehensions(self):
        [2 * x for x in self.data]


@timethem.timethem(('list', 'tuple', 'set', 'dict'), number=100,
                   plotparams={'filename': figpath + 'test_container.gif'})
class TestContainer(unittest.TestCase):
    def setUp(self, container_type):
        size = 1000
        self.key = size
        data = list(range(size))
        self.data = {
                'list': data,
                'tuple': tuple(data),
                'set': set(data),
                'dict': dict(zip(data, data))
                }[container_type]

    def test_in(self):
        self.key in self.data

if __name__ == '__main__':
    timethem.main()
