from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import unittest2
from builtins import *  # noqa

from typus.utils import idict, splinter


class IdictTest(unittest2.TestCase):
    def setUp(self):
        self.source = {'A': 0, 'b': 1}
        self.compare = {'a': 0, 'b': 1}

    def test_create_from_dict(self):
        target = idict(self.source)
        self.assertEqual(self.compare, target)
        self.assertNotEqual(self.source, target)

    def test_create_from_seq(self):
        target = idict(self.source.items())
        self.assertEqual(self.compare, target)
        self.assertNotEqual(self.source, target)

    def test_create_from_kwargs(self):
        target = idict(**self.source)
        self.assertEqual(self.compare, target)
        self.assertNotEqual(self.source, target)

    def test_create_from_dict_and_kwargs(self):
        target = idict(self.source, B=1)
        self.assertEqual(self.compare, target)


class SplinterTest(unittest2.TestCase):
    def test_basic(self):
        split = splinter(',')
        self.assertEqual(split('a, b,c'), ['a', 'b', 'c'])
        self.assertEqual(split('a, b\,c'), ['a', 'b,c'])

    def test_junk_delimiter(self):
        with self.assertRaises(ValueError):
            splinter('\\')

        with self.assertRaises(ValueError):
            splinter('\\  ')

        with self.assertRaises(ValueError):
            splinter('  ')

    def test_positional_spaces(self):
        split = splinter(';')
        self.assertEqual(split(' a; b;c'), ['a', 'b', 'c'])
        self.assertEqual(split(' a; b ;c'), ['a', 'b', 'c'])
        self.assertEqual(split(' a; b ;c '), ['a', 'b', 'c'])

    def test_delimiter_with_spaces(self):
        split = splinter(' @  ')
        self.assertEqual(split('a@ b@ c '), ['a', 'b', 'c'])

    def test_regex_delimiter(self):
        split = splinter('$')
        self.assertEqual(split('a$b$c'), ['a', 'b', 'c'])

    def test_doesnt_remove_other_slashes(self):
        split = splinter('*')
        self.assertEqual(split('a * b * c\*c \\b'), ['a', 'b', 'c*c \\b'])
