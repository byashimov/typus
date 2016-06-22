from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import unittest
from builtins import *  # noqa

import mock
from typus import TypusBase, typus


class TypusTest(unittest.TestCase):
    @mock.patch('typus.typus.chained_procs')
    def test_empty(self, mock_chained_procs):
        self.assertEqual(typus(''), '')
        mock_chained_procs.assert_not_called()

    def test_debug(self):
        self.assertEqual(typus('2mm', debug=True), '2_mm')


class TypusBaseTest(unittest.TestCase):
    def test_empty(self):
        class Testus(TypusBase):
            pass

        with self.assertRaises(AssertionError):
            Testus()
