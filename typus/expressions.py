# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
from builtins import *  # noqa

from .chars import *  # noqa
from .utils import map_choices


class EnRuExpressions(object):
    expressions = (
        'spaces linebreaks complex_symbols mdash sprime dprime phones '
        'digit_spaces pairs units ranges vulgar_fractions math ruabbr ruble '
        'positional_spaces'
    ).split()

    # Any unicode word
    words = r'[^\W\d_]'

    complex_symbols = {
        '...': '…',
        '<-': '←',
        '->': '→',
        '+-': '±',
        '+' + MINUS: '±',
        '<=': '≤',
        '>=': '≥',
        '/=': '≠',
        '(r)': '®',
        '(c)': '©',
        '(tm)': '™',
        # cyrillic
        '(с)': '©',
        '(тм)': '™',
    }

    vulgar_fractions = {
        '1/2': '½',
        '1/3': '⅓',
        '1/5': '⅕',
        '1/6': '⅙',
        '1/8': '⅛',
        '2/3': '⅔',
        '2/5': '⅖',
        '3/4': '¾',
        '3/5': '⅗',
        '3/8': '⅜',
        '4/5': '⅘',
        '5/6': '⅚',
        '5/8': '⅝',
        '7/8': '⅞',
    }

    math = {
        '-': MINUS,
        '*xх': TIMES,
    }

    # Not need to put >=, +-, etc, after expr_complex_symbols
    math_operators = (r'[\-{0}\*xх{1}\+\=±≤≥≠÷\/]'.format(MINUS, TIMES))

    positional_spaces = {
        # No need to put vulgar fractions in here because of expr_digit_spaces
        # which joines digits and words afterward
        'after': '←$€£%±≤≥≠{0}{1}©'.format(MINUS, TIMES),
        'both': '&',
        'before': '₽→®™' + MDASH,
    }

    # Adds space before ruble
    ruble = NBSP + '₽'

    def expr_spaces(self):
        # Doesn't work correctly with nbsp (replaces with space)
        expr = (
            (r'{0}{{2,}}'.format(ANYSP), WHSP),
        )
        return expr

    def expr_linebreaks(self):
        expr = (
            # Converts to unix-style
            (r'\r\n', '\n'),
            # Removes extra linebreaks
            (r'\n{2,}', '\n' * 2),
        )
        return expr

    def expr_complex_symbols(self):
        expr = (
            map_choices(self.complex_symbols),
        )
        return expr

    def expr_mdash(self):
        expr = (
            # Double dash guarantees to be replaced with mdash
            (r'{0}--{0}'.format(WHSP), MDASH_PAIR),

            # Dash can be between anything except digits
            # because in that case it's not obvious
            (r'{0}+\-{0}+(?!\d\b)'.format(ANYSP), MDASH_PAIR),

            # Same but backwards
            # It joins non-digit with digit or word
            (r'(\b\D+){0}+\-{0}+'.format(ANYSP, self.words),
             r'\1{0}'.format(MDASH_PAIR)),

            # Line beginning adds nbsp after dash
            (r'^\-{{1,2}}{0}+'.format(ANYSP),
             r'{0}{1}'.format(MDASH, NBSP)),

            # Also mdash can be at the end of the line in poems
            (r'{0}+\-{{1,2}}{0}*(?=$|<br/?>)'.format(ANYSP),
             r'{0}{1}'.format(NBSP, MDASH)),
        )
        return expr

    def expr_sprime(self):
        expr = (
            (r'(^|{0})(\d+)\''.format(ANYSP), r'\1\2' + SPRIME),
        )
        return expr

    def expr_dprime(self):
        # Won't break "4", but this will " 4", should be used with quotes
        expr = (
            (r'(^|{0})(\d+)"'.format(ANYSP), r'\1\2' + DPRIME),
        )
        return expr

    def expr_phones(self):
        expr = (
            (r'([0-9]{2,4})\-([0-9]{2,4})\-([0-9]{2,4})',
             r'\1{0}\2{0}\3'.format(NDASH)),
        )
        return expr

    def expr_digit_spaces(self):
        # Digits less than length 4 and following them words or digits
        # without comma
        expr = (
            (r'\b(\d{{1,3}}){0}(?=[0-9]+\b|{1}|{2})'
             .format(WHSP, self.words, self.math_operators), r'\1' + NBSP),
        )
        return expr

    def expr_pairs(self):
        # Only 1-2 symbols
        expr = (
            # Unions, units and all that small staff
            (r'\b({1}{{1,2}}){0}+'.format(WHSP, self.words), r'\1' + NBSP),
            # Fixes previous with leading dash or ellipsis
            (r'([-…]{1}{{1,2}}){0}'.format(NBSP, self.words), r'\1' + WHSP),
        )
        return expr

    def expr_units(self):
        # 1mm and 1 mm => 1_mm
        expr = (
            (r'\b(\d+{2}?){0}*({1}{{1,3}})\b'
                .format(WHSP, self.words, DPRIME),
             r'\1{0}\2'.format(NBSP)),
            # Reverts for some unitsm like: 3d, 2nd
            (r'\b(\d+){0}(nd|rd|th|d|g)\b'.format(NBSP), r'\1\2'),
        )
        return expr

    def expr_ranges(self):
        # Range: 2-3 => 2—3 -- no spaces!
        # Tries to not mess with minus:
        # skips if any math operator was found after range
        # or word after were wound
        expr = (
            (r'\b(\d+)\-(?!(?:\d+{0}+{1}|{2}))'
             .format(ANYSP, self.math_operators, self.words),
             r'\1{0}'.format(MDASH)),
        )
        return expr

    def expr_vulgar_fractions(self):
        # \b to exclude complex digits like 11/22
        expr = (
            map_choices(self.vulgar_fractions, r'\b({0})\b'),
        )
        return expr

    def expr_math(self):
        expr = (
            # Between digits or before single one: "3 - 3" and "-3"
            # Should run after mdash and phone.
            (r'(^|\d{0}*|{0}*)[{1}]({0}*\d)'.format(ANYSP, re.escape(x)),
             r'\1{0}\2'.format(y)) for x, y in self.math.items()
        )
        return expr

    def expr_ruabbr(self):
        # Fixes spaces between: т.д, т.п., т.ч., т.о., т.е.
        expr = (
            (r'\bт\.{1}*(?=[дпчео]\.)'.format(ANYSP, WHSP),
             r'т.{0}'.format(NBSP)),
        )
        return expr

    def expr_ruble(self):
        # Warning! Replaces dot at the end of sentence!
        expr = (
            (r'(\d){0}*(?:руб|р)\b\.?'.format(ANYSP),
             r'\1{0}'.format(self.ruble)),
        )
        return expr

    def expr_positional_spaces(self):
        both = self.positional_spaces['both']
        before = re.escape(self.positional_spaces['before'] + both)
        after = re.escape(self.positional_spaces['after'] + both)
        expr = (
            (r'{0}+([{1}])'.format(WHSP, before), NBSP + r'\1'),
            (r'([{1}]){0}+'.format(WHSP, after), r'\1' + NBSP),
        )
        return expr
