# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import *  # noqa

import unittest2
from typus.chars import *  # noqa
from typus.core import TypusCore
from typus.mixins import EnRuExpressions
from typus.processors import Expressions


class EnRuExpressionsTestCommon(object):
    """
    Common cases for solo and summary tests.
    """

    def typus(self, expression):
        class Testus(EnRuExpressions, TypusCore):
            processors = (Expressions, )
            expressions = (expression, )

        testus = Testus()
        return lambda text, test: self.assertEqual(testus(text), test)

    def test_names(self):
        # Makes sure all tests are exist
        for name in EnRuExpressions.expressions:
            self.assertTrue(hasattr(self, 'test_' + name),
                            '`{0}` test not found.'.format(name))

    def test_spaces(self):
        test = self.typus('spaces')
        test('foo{0}bar'.format(' ' * 30), 'foo bar')

    def test_linebreaks(self):
        test = self.typus('linebreaks')
        test('a\nb', 'a\nb')
        test('a\r\nb', 'a\nb')
        test('a{0}b'.format('\n' * 5), 'a\n\nb')
        test('a\n\n\r\nb', 'a\n\nb')

    def test_apostrophe(self):
        test = self.typus('apostrophe')
        test('She\'d', 'She{0}d'.format(RSQUO))
        test('I\'m', 'I{0}m'.format(RSQUO))
        test('it\'s', 'it{0}s'.format(RSQUO))
        test('don\'t', 'don{0}t'.format(RSQUO))
        test('you\'re', 'you{0}re'.format(RSQUO))
        test('he\'ll', 'he{0}ll'.format(RSQUO))
        test('90\'s', '90{0}s'.format(RSQUO))
        test('Карло\'s', 'Карло{0}s'.format(RSQUO))

    def test_mdash(self):
        test = self.typus('mdash')
        test('--', '--')
        test(', - foo', ',{0}foo'.format(MDASH_PAIR))
        test('foo - foo', 'foo{0}foo'.format(MDASH_PAIR))
        # if line begins, adds nbsp after mdash
        test('-- foo', '{1}{0}foo'.format(NBSP, MDASH))
        # if line ends, adds nbsp before mdash
        test('foo --', 'foo{0}{1}'.format(NBSP, MDASH))
        test('foo -- bar', 'foo{0}bar'.format(MDASH_PAIR))
        test(', -- foo', ',{0}foo'.format(MDASH_PAIR))
        # Python markdown replaces dash with ndash, don't know why
        test('foo {0} foo'.format(NDASH), 'foo{0}foo'.format(MDASH_PAIR))
        return test

    def test_primes(self):
        test = self.typus('primes')
        test('4\'', '4' + SPRIME)
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
        test('I’ll check', 'I’ll check')
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
        # Exceptions
        test('3g', '3g')  # 4G lte
        test('3d', '3d')  # 3D movie
        test('2nd', '2nd')  # floor
        test('3rd', '3rd')  # floor
        test('4th', '4th')  # floor
        test('1px', '1px')

    def test_ranges(self):
        test = self.typus('ranges')
        test('25-foo', '25-foo')
        test('2-3', '2{0}3'.format(MDASH))
        test('2,5-3', '2,5{0}3'.format(MDASH))
        test('0.5-3', '0.5{0}3'.format(MDASH))
        return test

    def test_complex_symbols(self):
        test = self.typus('complex_symbols')
        for key, value in EnRuExpressions.complex_symbols.items():
            test(key, value)
        # Case insensitive test
        test('(C)', '©')

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

    def test_abbrs(self):
        test = self.typus('abbrs')
        test('т. д.', 'т.{0}д.'.format(NNBSP))
        test('т.д.', 'т.{0}д.'.format(NNBSP))
        test('т.п.', 'т.{0}п.'.format(NNBSP))
        test('т. ч.', 'т.{0}ч.'.format(NNBSP))
        test('т.е.', 'т.{0}е.'.format(NNBSP))
        test('Пушкин А.С.', 'Пушкин А.{0}С.'.format(NNBSP))
        test('А.С. Пушкин', 'А.{0}С.{1}Пушкин'.format(NNBSP, NBSP))

    def test_ruble(self):
        test = self.typus('ruble')
        test('111 р', '111{0}₽'.format(NBSP))
        test('111 р.', '111{0}₽'.format(NBSP))
        test('111 руб', '111{0}₽'.format(NBSP))
        test('111 руб.', '111{0}₽'.format(NBSP))
        return test

    def _positional_spaces(self, attr, find, replace):
        test = self.typus(attr)

        result = {
            'after': 'foo {0}_bar',
            'both': 'foo_{0}_bar',
            'before': 'foo_{0} bar',
        }

        for direction, chars in getattr(EnRuExpressions, attr).items():
            pattern = result[direction]
            for char in chars:
                string = pattern.format(char)
                test(string.replace('_', find), string.replace('_', replace))

    def test_rep_positional_spaces(self):
        self._positional_spaces('rep_positional_spaces', WHSP, NBSP)

    def test_del_positional_spaces(self):
        self._positional_spaces('del_positional_spaces', WHSP, '')


class EnRuExpressionsTest(EnRuExpressionsTestCommon, unittest2.TestCase):
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

        # Float
        test('0,5-3', '0,5{0}3'.format(MDASH))
        test('-0,5-3', '-0,5{0}3'.format(MDASH))
        test('-5.5-3', '-5.5{0}3'.format(MDASH))
        test('-5,5-3', '-5,5{0}3'.format(MDASH))
        test('-5,5-3.5', '-5,5{0}3.5'.format(MDASH))

        # Skips
        test('2 - 3', '2 - 3')
        test('2-3 x 4', '2-3 x 4')
        test('2-3 * 4', '2-3 * 4')
        test('2-3 - 4', '2-3 - 4')

        # Left is less than or equal to right
        test('3-2', '3-2')
        test('3-3', '3-3')

    def test_pairs(self):
        test = super(EnRuExpressionsTest, self).test_pairs()
        test('aaa 2a', 'aaa 2a')  # letters only, no digits

    def test_digit_spaces(self):
        test = super(EnRuExpressionsTest, self).test_digit_spaces()
        test('444 -', '444{0}-'.format(NBSP))
        test('4444444 foo', '4444444 foo')

    def test_primes(self):
        test = super(EnRuExpressionsTest, self).test_primes()
        test('"4"', '"4"')
