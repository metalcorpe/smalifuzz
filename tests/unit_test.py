# -*- coding: utf-8 -*-

import unittest

from smalifuzz.helpers import (dictionary_serializer, recursive_dict_sort,
                               removeLevel)


class UnitTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_removeLevel_success(self):
        dictionary_target = {"b": "c"}
        dictionary_initial = {"a": {"b": "c"}}
        dictionary_after = removeLevel(dictionary_initial, 0)
        self.assertEqual(dictionary_after, dictionary_target)

    def test_recursive_dict_sort_success(self):
        dictionary_target = {"a": {"a": [1, 2], "b": [1, 2]}}
        dictionary_initial = {"a": {"b": [2, 1], "a": [2, 1]}}
        dictionary_after = recursive_dict_sort(dictionary_initial)
        self.assertEqual(dictionary_after, dictionary_target)

    def test_dictionary_serializer_success(self):
        dictionary_target = "aparam0param1returnType"
        dictionary_initial = {"a":{"params":["param0","param1"], "return":"returnType"}}
        dictionary_after = dictionary_serializer(dictionary_initial)
        self.assertEqual(dictionary_after, dictionary_target)
