from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import *  # noqa

import mock
import unittest2
from typus import TypusCore, ru_typus


class TypusTest(unittest2.TestCase):
    @mock.patch('typus.ru_typus.process')
    def test_empty(self, mock_process):
        self.assertEqual(ru_typus(''), '')
        mock_process.assert_not_called()

    def test_debug(self):
        self.assertEqual(ru_typus('2mm', debug=True), '2_mm')


class BaseTypusTest(unittest2.TestCase):
    def test_empty(self):
        class Testus(TypusCore):
            pass

        with self.assertRaises(AssertionError):
            Testus()
