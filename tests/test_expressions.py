# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import unittest
from builtins import *  # noqa

from typus.base import TypusBase
from typus.chars import *  # noqa
from typus.expressions import EnRuExpressions


class EnRuExpressionsTestCommon(object):
    """
    Common cases for solo and summary tests.
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
        test('-- ', MDASH + NBSP)  # if line begins, adds nbsp after mdash
        test(' --', NBSP + MDASH)  # if line ends, adds nbsp before mdash
        test(' -- ', MDASH_PAIR)
        test(', -- ', ',' + MDASH_PAIR)
        test(', - foo', ',{0}foo'.format(MDASH_PAIR))
        test('foo - foo', 'foo{0}foo'.format(MDASH_PAIR))
        return test

    def test_sprime(self):
        test = self.typus('sprime')
        test('4\'', '4' + SPRIME)

    def test_dprime(self):
        test = self.typus('dprime')
        test('4"', '4' + DPRIME)
        test('" 22"', '" 22' + DPRIME)
        return test

    def test_phones(self):
        test = self.typus('phones')
        test('555-55-55', '555{0}55{0}55'.format(NDASH))
        test('55-555-55', '55{0}555{0}55'.format(NDASH))
        return test

    def test_digit_spaces(self):
        test = self.typus('digit_spaces')
        test('4444444 fooo', '4444444 fooo')
        test('444 foo', '444{0}foo'.format(NBSP))
        test('444 +', '444{0}+'.format(NBSP))
        test('444 4444 bucks', '444{0}4444 bucks'.format(NBSP))
        return test

    def test_pairs(self):
        test = self.typus('pairs')
        test('aaa aaa', 'aaa aaa')
        test('aaa-aa aa', 'aaa-aa aa')  # important check -- dash and 2 letters
        test('aaa aa', 'aaa aa')
        test('a aa a', 'a{0}aa{0}a'.format(NBSP))
        return test

    def test_units(self):
        test = self.typus('units')
        # Latin
        test('1mm', '1{0}mm'.format(NBSP))
        test('1 mm', '1{0}mm'.format(NBSP))
        test('1dpi', '1{0}dpi'.format(NBSP))
        # Cyrillic
        test('1кг', '1{0}кг'.format(NBSP))
        # Skips
        test('1foobar', '1foobar')
        # Reverts
        test('3g', '3g')  # 4G lte
        test('3d', '3d')  # 3D movie
        test('2nd', '2nd')  # floor
        test('3rd', '3rd')  # floor
        test('4th', '4th')  # floor

    def test_ranges(self):
        test = self.typus('ranges')
        test('25-foo', '25-foo')
        test('2-3', '2{0}3'.format(MDASH))
        return test

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
        test('111 р', '111{0}₽'.format(NBSP))
        test('111 р.', '111{0}₽'.format(NBSP))
        test('111 руб', '111{0}₽'.format(NBSP))
        test('111 руб.', '111{0}₽'.format(NBSP))
        return test

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


class EnRuExpressionsTest(unittest.TestCase, EnRuExpressionsTestCommon):
    """
    Tests expressions one by one.
    Some of them may return different results depending on which was
    applied earlier, so order matters. But that also means it's important
    to be sure they don't affect each other more than expected. This case
    tests every expression as if it was the only one to apply.
    """
    def test_mdash(self):
        test = super(EnRuExpressionsTest, self).test_mdash()
        test('foo - "11" 00', 'foo{0}"11" 00'.format(MDASH_PAIR))
        test('2 - 2foo', '2{0}2foo'.format(MDASH_PAIR))
        test('2 - 2', '2 - 2')  # Doesn't clash with minus

    def test_phones(self):
        test = super(EnRuExpressionsTest, self).test_phones()
        test('55-555', '55-555')  # skips

    def test_ranges(self):
        test = super(EnRuExpressionsTest, self).test_ranges()
        test('2-3 foo', '2{0}3 foo'.format(MDASH))
        test('(15-20 items)', '(15{0}20 items)'.format(MDASH))

        # Skips
        test('2 - 3', '2 - 3')
        test('2-3 x 4', '2-3 x 4')
        test('2-3 * 4', '2-3 * 4')
        test('2-3 - 4', '2-3 - 4')

    def test_pairs(self):
        test = super(EnRuExpressionsTest, self).test_pairs()
        test('aaa 2a', 'aaa 2a')  # letters only, no digits

    def test_digit_spaces(self):
        test = super(EnRuExpressionsTest, self).test_digit_spaces()
        test('444 -', '444{0}-'.format(NBSP))
        test('4444444 foo', '4444444 foo')

    def test_dprime(self):
        test = super(EnRuExpressionsTest, self).test_dprime()
        test('"4"', '"4"')
