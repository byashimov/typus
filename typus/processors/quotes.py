from itertools import cycle
from typing import Match

from ..chars import DLQUO, LAQUO, LDQUO, LSQUO, RAQUO, RDQUO, RSQUO
from ..utils import re_compile
from .base import BaseProcessor


class BaseQuotes(BaseProcessor):
    """
    Replaces regular quotes with typographic ones.
    Supports any level nesting, but doesn't work well with minutes ``1'``
    and inches ``1"`` within the quotes, that kind of cases are ignored.
    Please, provide ``loq, roq, leq, req`` attributes with custom quotes.

    >>> from typus import en_typus
    >>> en_typus('Say "what" again!')
    'Say “what” again!'
    """

    loq = roq = leq = req = NotImplemented

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pairs of odd and even quotes. Already *switched* in one dimension.
        # See :meth:`_switch_nested` for more help.
        self.switch = (self.loq + self.req, self.leq + self.roq)

        # Replaces all quotes with `'`
        quotes = ''.join((LSQUO, RSQUO, LDQUO, RDQUO, DLQUO, LAQUO, RAQUO))
        self.re_normalize = re_compile(r'[{0}]'.format(quotes))

        # Matches nested quotes (with no quotes within)
        # and replaces with odd level quotes
        self.re_normal = re_compile(
            # No words before
            r'(?<!\w)'
            # Starts with quote
            r'(["\'])'
            r'(?!\s)'
            # Everything but quote inside
            r'((?!\1).+?)'
            r'(?!\s)'
            # Ends with same quote from the beginning
            r'\1'
            # No words afterwards
            r'(?!\w)'
        )
        self.re_normal_replace = r'{0}\2{1}'.format(self.loq, self.roq)

        # Matches with typo quotes
        self.re_nested = re_compile(r'({0}|{1})'.format(self.loq, self.roq))

    def run(self, text: str, **kwargs) -> str:
        # Normalizes editor's quotes to double one
        normalized = self.re_normalize.sub('\'', text)

        # Replaces normalized quotes with first level ones, starting
        # from inner pairs, moves to sides
        nested = 0
        while True:
            normalized, replaced = self.re_normal.subn(
                self.re_normal_replace, normalized)
            if not replaced:
                break
            nested += 1

        # Saves some cpu :)
        # Most cases are about just one level quoting
        if nested < 2:
            return self.run_other(normalized, **kwargs)

        # At this point all quotes are of odd type, have to fix it
        switched = self._switch_nested(normalized)
        return self.run_other(switched, **kwargs)

    def _switch_nested(self, text: str):
        """
        Switches nested quotes to another type.
        This function stored in a separate method to make possible to mock it
        in tests to make sure it doesn't called without special need.
        """

        # Stores a cycled pairs of possible quotes. Every other loop it's
        # switched to provide *next* type of a given quote
        quotes = cycle(self.switch)

        def replace(match: Match):
            # Since only odd quotes are matched, comparison is the way to
            # choose whether it's left or right one of type should be returned.
            # As the first quote is the left one, makes negative equal which
            # return false, i.e. zero index
            return next(quotes)[match.group() != self.loq]
        return self.re_nested.sub(replace, text)


class EnQuotes(BaseQuotes):
    r"""
    Provides English quotes configutation for :class:`typus.processors.Quotes`
    processor.

    >>> from typus import en_typus
    >>> en_typus('He said "\'Winnie-the-Pooh\' is my favorite book!".')
    'He said “‘Winnie-the-Pooh’ is my favorite book!”.'
    """

    # Left odd, right odd, left even, right even
    loq = LDQUO
    roq = RDQUO
    leq = LSQUO
    req = RSQUO


class RuQuotes(BaseQuotes):
    r"""
    Provides Russian quotes configutation for :class:`typus.processors.Quotes`
    processor.

    >>> from typus import ru_typus
    >>> ru_typus('Он сказал: "\'Винни-Пух\' -- моя любимая книга!".')
    'Он\xa0сказал: «„Винни-Пух“\u202f—\u2009моя любимая книга!».'
    """

    # Left odd, right odd, left even, right even
    loq = LAQUO
    roq = RAQUO
    leq = DLQUO
    req = LDQUO
