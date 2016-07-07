from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import unittest2
from builtins import *  # noqa

from typus.utils import idict


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
