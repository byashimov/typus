# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import unittest
from builtins import *  # noqa

import mock
from typus import Typus


class QuotesProcessorTest(unittest.TestCase):
    class Testus(Typus):
        expressions = ''

    def typus(self):
        typus = self.Testus()
        return lambda text, test: self.assertEqual(typus(text), test)

    @mock.patch('typus.processors.QuotesProcessor._fix_nesting',
                return_value='test')
    def test_fix_nesting_call(self, mock_fix_nesting):
        test = self.Testus()
        test('00 "11" 00')
        mock_fix_nesting.assert_not_called()

        test('"00 "11" 00"')
        mock_fix_nesting.assert_called_once()

    def test_quotes(self):
        test = self.typus()

        # Levels
        test('00 "11" 00', '00 «11» 00')  # One
        test('"00 "11" 00"', '«00 „11“ 00»')  # Two
        test('00" "11 "22" 11"', '00" «11 „22“ 11»')  # Tree

        # Hardcore
        test('00 ""22"" 00', '00 «„22“» 00')
        test('00 ""22..."" 00', '00 «„22...“» 00')
        test('00 ""22"..." 00', '00 «„22“...» 00')

        # Weired cases
        test('00 "... "22"" 00', '00 «... „22“» 00')
        with self.assertRaises(AssertionError):
            # This fails because matches to first group, sorry :(
            test('00 "..."22"" 00', '00 «...„22“» 00')

        # Punctuation
        test('00 "...11 "22!"" 00', '00 «...11 „22!“» 00')
        test('00 "11 "22!"..." 00', '00 «11 „22!“...» 00')
        test('00 "11 "22!"?!." 00', '00 «11 „22!“?!.» 00')
        test('00 "11 "22!"?!."? 00', '00 «11 „22!“?!.»? 00')

        # Nested on side
        test('00 ""22!" 11" 00', '00 «„22!“ 11» 00')
        test('00 "11 "22?"" 00', '00 «11 „22?“» 00')

        # Different quotes
        test('00 "“22”" 00', '00 «„22“» 00')
        test('00 "‘22’" 00', '00 «„22“» 00')

        # Inches, minutes are ignored within quotes
        test('00 "11\'" 00 "11"', '00 "11\'" 00 «11»')
        test('00" "11" 00 "11"', '00" «11» 00 «11»')

        # Fire them all!
        test('''00" "11 '22' 11"? "11 '22 "33 33"' 11" 00' "11 '22' 11" 00"''',
             '00" «11 „22“ 11»? «11 „22 «33 33»“ 11» 00\' «11 „22“ 11» 00"')

        # Html test
        test('<span>"11"</span>', '<span>«11»</span>')
        test('"<span>11</span>"', '«<span>11</span>»')
