# -*- coding:utf-8 -*-
"""
    author comger@gmail.com
"""
import json
from kpages import LogicContext, reflesh_config
from unittest import TestCase


class DemoCase(TestCase):
    """ 测试案例"""
    def setUp(self):
        pass

    def test_print(self):
        """ 打印测试 """
        self.assertEqual(1,2)


class Demo1Case(TestCase):
    def setUp(self):
        pass

    def test_insert(self):
        print bb
