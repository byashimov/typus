# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import *  # noqa
from itertools import cycle

from .chars import *  # noqa
from .utils import re_compile


class BaseProcessor(object):
    """
    Processors are almost like regular functions except they are initiated
    and stored inside Typus instance so they can pre-cache different stuff
    like regexps which could depend on Typus configurations
    """

    def __init__(self, typus):
        self.typus = typus


class QuotesProcessor(BaseProcessor):
    """
    Replaces regular quotes with typographic ones.
    Supports any level nesting, but doesn't work well with minutes (1')
    and inches (1") within quotes, that kind of cases are ignored.
    """

    # ?, !, ?!, ?.., !.., ..., …
    punctuation = r'(?:\.{1,3}|[?!…])'

    def __init__(self, *args, **kwargs):
        super(QuotesProcessor, self).__init__(*args, **kwargs)

        # Odd and even levels: left, right
        self.loq, self.roq = self.typus.loq, self.typus.roq
        self.leq, self.req = self.typus.leq, self.typus.req

        # Replaces all quotes with `"`
        quotes = ''.join((LSQUO, RSQUO, LDQUO, RDQUO, DLQUO, LAQUO, RAQUO))
        self.re_normalize = re_compile(r'[{0}]'.format(quotes))

        # Matches quotes on the toppest level (with no quotes within)
        # and replaces with odd level quotes
        self.re_pairs = re_compile(
            # Starts with quote
            r'(["\'])'
            # Word beginning or another _already_processed_ quote pair
            # or punctuation or html tag
            r'(\b|{0}|{2}|<)'
            # Everything but quote inside
            r'([^"\']+?)'
            # Word end or processed quote or punctuation ot html tag
            r'(\b|{1}|{2}|>)'
            # Ends with same quote from the beginnig
            r'\1'
            .format(self.loq, self.roq, self.punctuation))
        self.re_pairs_replace = r'{0}\2\3\4{1}'.format(self.loq, self.roq)

        # Matches to typo quotes
        self.re_typo_quotes = re_compile(r'({0}|{1}|[^{0}{1}]+)'
                                         .format(self.loq, self.roq))

    def __call__(self, source):
        if not source.strip():
            return source

        # Normalizes edtior's quotes to double one
        normalized = self.re_normalize.sub('"', source)

        # Replaces normalized quotes with first level ones, starting
        # from inner pairs, moves to sides
        nested = -1
        while True:
            normalized, replaced = self.re_pairs.subn(self.re_pairs_replace,
                                                      normalized)
            if not replaced:
                break
            nested += 1

        # Saves some cpu :)
        # Most cases are about just one level quoting
        if not nested:
            return normalized

        # At this point all quotes are of odd type, have to fix it
        fixed = self._fix_nesting(normalized)
        return fixed

    def _fix_nesting(self, normalized):
        # Toggles quotes for any other nesting pair
        pairs = cycle((self.loq + self.roq, self.leq + self.req))
        quoted, pair = '', None

        for match in self.re_typo_quotes.finditer(normalized):
            chunk = match.group(0)
            if chunk == self.loq:
                pair = next(pairs)
                chunk = pair[0]
            elif chunk == self.roq:
                chunk = pair[1]
                pair = next(pairs)
            quoted += chunk
        return quoted
