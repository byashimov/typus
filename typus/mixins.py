# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
from builtins import *  # noqa

from .chars import *  # noqa
from .utils import map_choices


class EnQuotes(object):
    # Quotes: left odd, right odd, left even, right even
    loq, roq, leq, req = LDQUO, RDQUO, LSQUO, RSQUO


class RuQuotes(object):
    loq, roq, leq, req = LAQUO, RAQUO, DLQUO, LDQUO


class EnRuExpressions(object):
    expressions = (
        'spaces linebreaks complex_symbols mdash sprime dprime phones '
        'digit_spaces pairs units ranges vulgar_fractions math ruble abbr '
        'rep_positional_spaces del_positional_spaces'
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
        '(p)': '℗',
        '(tm)': '™',
        '(sm)': '℠',
        # cyrillic
        '(с)': '©',
        '(р)': '℗',
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
    math_operators = r'[\-{0}\*xх{1}\+\=±≤≥≠÷\/]'.format(MINUS, TIMES)

    rep_positional_spaces = {
        # No need to put vulgar fractions in here because of expr_digit_spaces
        # which joins digits and words afterward
        'after': '←$€£%±≤≥≠{0}{1}©'.format(MINUS, TIMES),
        'both': '&',
        'before': '₽→' + MDASH,
    }

    del_positional_spaces = {
        'before': '®℗™℠:,.?!…',
    }

    # Adds space before ruble
    ruble = NBSP + '₽'

    def expr_spaces(self):
        # Doesn't work correctly with nbsp (replaces with space)
        expr = (
            (r'{0}{{2,}}'.format(ANYSP), WHSP),
            # trims spaces at the beginning and end of the line
            (r'(?:^{0}+|{0}+$)'.format(ANYSP), ''),
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
            (r'{0}+[\-|{1}]{0}+(?!\d\b)'.format(ANYSP, NDASH), MDASH_PAIR),

            # Same but backwards
            # It joins non-digit with digit or word
            (r'(\b\D+){0}+[\-|{1}]{0}+'.format(ANYSP, NDASH),
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
            (r'\b(\d+){0}*(?!(?:nd|rd|th|d|g|px)\b)({1}{{1,3}})\b'
             .format(WHSP, self.words),
             r'\1{0}\2'.format(NBSP)),
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

    def expr_abbr(self):
        # Fixes spaces between shorten words
        expr = (
            (r'\b({1}\.){0}*(?={1})'.format(WHSP, self.words),
             r'\1{0}'.format(NBSP)),
        )
        return expr

    def expr_ruble(self):
        # Warning! Replaces dot at the end of sentence!
        expr = (
            (r'(\d){0}*(?:руб|р)\b\.?'.format(ANYSP),
             r'\1{0}'.format(self.ruble)),
        )
        return expr

    def _positional_spaces(self, data, find, replace):
        both = data.get('both', '')
        before = re.escape(data.get('before', '') + both)
        after = re.escape(data.get('after', '') + both)
        expr = []
        if before:
            expr.append((r'{0}+(?=[{1}])'.format(find, before), replace))
        if after:
            expr.append((r'(?<=[{1}]){0}+'.format(find, after), replace))
        return expr

    def expr_rep_positional_spaces(self):
        """
        Replaces whitespaces after or before character
        with non-breakable space.
        """
        expr = self._positional_spaces(self.rep_positional_spaces, WHSP, NBSP)
        return expr

    def expr_del_positional_spaces(self):
        """
        Deletes any spaces before or after character.
        """
        expr = self._positional_spaces(self.del_positional_spaces, ANYSP, '')
        return expr
