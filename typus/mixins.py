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
        'spaces linebreaks complex_symbols mdash primes phones digit_spaces '
        'pairs units ranges vulgar_fractions math ruble abbrs '
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

    # Replace this if you don't need nbsp before ruble
    ruble = NBSP + '₽'

    def expr_spaces(self):
        """
        Trims spaces at the beginning and end of the line and remove extra
        spaces within.
        **NOTE**: Doesn't work correctly with nbsp (replaces with space).
        """

        expr = (
            (r'{0}{{2,}}'.format(ANYSP), WHSP),
            (r'(?:^{0}+|{0}+$)'.format(ANYSP), ''),
        )
        return expr

    def expr_linebreaks(self):
        """
        Converts line breaks to unix-style and removes extra breaks
        if found more than two in a row.
        """

        expr = (
            (r'\r\n', '\n'),
            (r'\n{2,}', '\n' * 2),
        )
        return expr

    def expr_complex_symbols(self):
        """
        Replaces complex symbols with appropriate unicode symbols:
        `(c)` becomes `©`.
        """

        expr = (
            map_choices(self.complex_symbols),
        )
        return expr

    def expr_mdash(self):
        """
        Replaces dash with mdash.
        """

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

    def expr_primes(self):
        """
        Replaces quotes with single and double primes.
        **NOTE**: Won't break "4", but this will " 4", should be used after
        `quotes`.
        """

        expr = (
            (r'(^|{0})(\d+)\''.format(ANYSP), r'\1\2' + SPRIME),
            (r'(^|{0})(\d+)"'.format(ANYSP), r'\1\2' + DPRIME),
        )
        return expr

    def expr_phones(self):
        """
        Replaces dash with ndash in phone numbers which should be a trio of
        2-4 length digits:
        888-00-00
        00-888-00
        00-00-888
        """

        expr = (
            (r'([0-9]{2,4})\-([0-9]{2,4})\-([0-9]{2,4})',
             r'\1{0}\2{0}\3'.format(NDASH)),
        )
        return expr

    def expr_digit_spaces(self):
        """
        Replaces whitespace with non-breakable space after 4 (and less)
        length digits if word or digit without comma or math operators
        found afterwards:
        3 apples
        40 000 bucks
        400 + 3
        Skips:
        4000 bucks
        40 000,00 bucks
        """

        expr = (
            (r'\b(\d{{1,3}}){0}(?=[0-9]+\b|{1}|{2})'
             .format(WHSP, self.words, self.math_operators), r'\1' + NBSP),
        )
        return expr

    def expr_pairs(self):
        """
        Replaces whitespace with non-breakable space after 1-2 length words.
        """

        expr = (
            # Unions, units and all that small staff
            (r'\b({1}{{1,2}}){0}+'.format(WHSP, self.words), r'\1' + NBSP),
            # Fixes previous with leading dash or ellipsis
            (r'([-…]{1}{{1,2}}){0}'.format(NBSP, self.words), r'\1' + WHSP),
        )
        return expr

    def expr_units(self):
        """
        Puts non-breakable space between digits and units:
        `1mm` and `1 mm` becomes `1_mm`
        """

        expr = (
            (r'\b(\d+){0}*(?!(?:nd|rd|th|d|g|px)\b)({1}{{1,3}})\b'
             .format(WHSP, self.words),
             r'\1{0}\2'.format(NBSP)),
        )
        return expr

    def expr_ranges(self):
        """
        Replaces dash with mdash in ranges.
        Tries to not mess with minus: skips if any math operator or word
        was found after dash.
        **NOTE**: _range_ should not have spaces between dash: `2-3`.
        """

        expr = (
            (r'\b(\d+)\-(?!(?:\d+{0}+{1}|{2}))'
             .format(ANYSP, self.math_operators, self.words),
             r'\1{0}'.format(MDASH)),
        )
        return expr

    def expr_vulgar_fractions(self):
        """
        Replaces vulgar fractions with appropriate unicode symbols.
        """

        expr = (
            # \b to excludes digits which are not on map, like `11/22`
            map_choices(self.vulgar_fractions, r'\b({0})\b'),
        )
        return expr

    def expr_math(self):
        """
        Puts minus and multiplication symbols between pair and before
        single digits:
        3 - 3 = 0
        -3 degrees
        3 × 3 = 9
        ×3 faster!
        **NOTE**: Should run after `mdash` and `phones`.
        """

        expr = (
            (r'(^|\d{0}*|{0}*)[{1}]({0}*\d)'.format(ANYSP, re.escape(x)),
             r'\1{0}\2'.format(y)) for x, y in self.math.items()
        )
        return expr

    def expr_abbrs(self):
        """
        Adds non-breakable space and replaces whitespaces between
        shorten words.
        """

        expr = (
            (r'\b({1}\.){0}*(?={1})'.format(WHSP, self.words),
             r'\1{0}'.format(NBSP)),
        )
        return expr

    def expr_ruble(self):
        """
        Replaces `руб` and `р` (with or without dot) after digits
        with ruble symbol.
        **NOTE**: If pattern found at the end of the sentence this will break
        things up, because it drops the dot.
        """

        expr = (
            (r'(\d){0}*(?:руб|р)\b\.?'.format(ANYSP),
             r'\1{0}'.format(self.ruble)),
        )
        return expr

    def _positional_spaces(self, data, find, replace):
        """
        Helper method for `rep_positional_spaces` and `del_positional_spaces`
        expressions.
        """

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
        Replaces whitespaces after and before certain symbols
        with non-breakable space.
        """

        expr = self._positional_spaces(self.rep_positional_spaces, WHSP, NBSP)
        return expr

    def expr_del_positional_spaces(self):
        """
        Removes spaces before and after certain symbols.
        """

        expr = self._positional_spaces(self.del_positional_spaces, ANYSP, '')
        return expr
