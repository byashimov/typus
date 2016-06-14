# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import unittest
from builtins import *  # noqa

from typus.base import TypusBase
from typus.chars import *  # noqa
from typus.expressions import EnRuExpressions


class EnRuExpressionsTest(unittest.TestCase):
    """
    Tests expressions one by one.
    Some of them may return different results depending on which was
    applied earlier, so order matters. But that also means it's important
    to be sure they don't affect each other more than expected. This case
    tests every expression as if it was the only one to apply.
    """

    def typus(self, expression):
        class Testus(TypusBase, EnRuExpressions):
            expressions = (expression,)

        testus = Testus()
        return lambda text, test: self.assertEqual(testus(text), test)

    def test_names(self):
        # Makes sure all tests are exist
        for name in EnRuExpressions.expressions:
            self.assertTrue(hasattr(self, 'test_' + name))

    def test_spaces(self):
        test = self.typus('spaces')
        test(' ' * 30, ' ')

    def test_linebreaks(self):
        test = self.typus('linebreaks')
        test('\n', '\n')
        test('\r\n', '\n')
        test('\n' * 5, '\n\n')
        test('\n\n\r\n', '\n\n')

    def test_mdash(self):
        test = self.typus('mdash')
        test('--', '--')
        test('-- ', MDASH + NBSP)
        test(' -- ', MDASH_PAIR)
        test(', -- ', ',' + MDASH_PAIR)
        test(', - foo', ',{0}foo'.format(MDASH_PAIR))

    def test_sprime(self):
        test = self.typus('sprime')
        test('4\'', '4' + SPRIME)

    def test_dprime(self):
        test = self.typus('dprime')
        test('4"', '4' + DPRIME)

    def test_phones(self):
        test = self.typus('phones')
        test('555-55-55', '555{0}55{0}55'.format(NDASH))
        test('55-555-55', '55{0}555{0}55'.format(NDASH))
        # Skips
        test('55-555', '55-555')

    def test_digit_spaces(self):
        test = self.typus('digit_spaces')
        test('4444444 foo', '4444444 foo')
        test('444 foo', '444{0}foo'.format(NBSP))
        test('444 +', '444{0}+'.format(NBSP))
        test('444 -', '444{0}-'.format(NBSP))

    def test_pairs(self):
        test = self.typus('pairs')
        test('aaa aaa', 'aaa aaa')
        test('aaa 2a', 'aaa 2a')  # letters only, no digits
        test('aaa-aa aa', 'aaa-aa aa')  # important check -- dash and 2 letters
        test('aaa aa', 'aaa aa')
        test('a aa a', 'a{0}aa{0}a'.format(NBSP))

    def test_units(self):
        test = self.typus('units')
        # Latin
        test('1mm', '1{0}mm'.format(NBSP))
        test('1 mm', '1{0}mm'.format(NBSP))
        test('1dpi', '1{0}dpi'.format(NBSP))
        test('1g', '1{0}g'.format(NBSP))
        # Cyrillic
        test('1кг', '1{0}кг'.format(NBSP))
        # Skips
        test('1foobar', '1foobar')

    def test_ranges(self):
        test = self.typus('ranges')
        test('2-3', '2{0}3'.format(MDASH))
        test('2-3 44', '2{0}3 44'.format(MDASH))
        test('2 - 3', '2 - 3')
        test('2-3 x 4', '2-3 x 4')
        test('2-3 * 4', '2-3 * 4')
        test('2-3 = 4', '2-3 = 4')
        test('2-3 / 4', '2-3 / 4')
        test('2-3 - 4', '2-3 - 4')

    def test_complex_symbols(self):
        test = self.typus('complex_symbols')
        for key, value in EnRuExpressions.complex_symbols.items():
            test(key, value)

    def test_vulgar_fractions(self):
        test = self.typus('vulgar_fractions')
        for key, value in EnRuExpressions.vulgar_fractions.items():
            test(key, value)
        test('1/4', '1/4')  # there is not such a char

    def test_math(self):
        test = self.typus('math')
        for options, result in EnRuExpressions.math.items():
            for option in options:
                # -3, 3-3, 3 - 3, x - 3
                test(option + '3', result + '3')
                test('3{0}3'.format(option), '3{0}3'.format(result))
                test('3 {0} 3'.format(option), '3 {0} 3'.format(result))
                test('x {0} 3'.format(option), 'x {0} 3'.format(result))

    def test_ruabbr(self):
        test = self.typus('ruabbr')
        test('т. д.', 'т.{0}д.'.format(NBSP))
        test('т.д.', 'т.{0}д.'.format(NBSP))
        test('т.п.', 'т.{0}п.'.format(NBSP))
        test('т. ч.', 'т.{0}ч.'.format(NBSP))
        test('т.е.', 'т.{0}е.'.format(NBSP))

    def test_ruble(self):
        test = self.typus('ruble')
        test('111 руб.', '111{0}₽'.format(NBSP))
        test('111 рублей', '111 рублей')

    def test_positional_spaces(self):
        test = self.typus('positional_spaces')

        result = {
            'after': ' {0}' + NBSP,
            'both': NBSP + '{0}' + NBSP,
            'before': NBSP + '{0} ',
        }

        for direction, chars in EnRuExpressions.positional_spaces.items():
            pattern = result[direction]
            for char in chars:
                string = pattern.format(char)
                test(string.replace(NBSP, WHSP), string)
