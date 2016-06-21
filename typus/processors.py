# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import *  # noqa
from functools import wraps
from itertools import count, cycle

from .chars import *  # noqa
from .utils import re_compile


class BaseProcessor(object):
    """
    Processors are almost like regular functions except they are initiated
    and stored inside Typus instance so they can pre-cache different stuff
    like regexps which could depend on Typus configuration
    """

    def __init__(self, typus):
        self.typus = typus


class EscapeHtml(BaseProcessor):
    """
    Extracts html tags and puts them back after
    typus processed.
    Warning: doesn't support nested code tags.
    """

    html_patterns = (
        re_compile(r'(<)(head|iframe|pre|code|script|style)(.*?>.*?</\2>)'),
        # Doctype, xml, closing tag, any tag
        re_compile(r'(<[\!\?/]?[a-z]+.*?>)'),
        # Comments
        re_compile(r'(<\!\-\-.*?\-\->)'),
    )
    html_placeholder = '<codeblock{0}>'

    def __call__(self, func):
        @wraps(func)
        def inner(text, *args, **kwargs):
            escaped = text
            storage = []
            uid = count()
            for pattern in self.html_patterns:
                escaped = pattern.sub(
                    self._save_html(storage, uid), escaped)

            # Runs typus
            processed = func(escaped, *args, **kwargs)
            if not storage:
                return processed

            restored = self._restore_html(storage, processed)
            return restored
        return inner

    def _save_html(self, storage, uid):
        def replace(match):
            key = self.html_placeholder.format(next(uid))
            html = ''.join(match.groups())
            storage.append((key, html))
            return key
        return replace

    def _restore_html(self, storage, text):
        """
        This one could be static or even direclty placed in __call__
        but I need to know if it's called or not in mocked cases
        because coverage.py returnes summary report
        """
        for key, value in reversed(storage):
            text = text.replace(key, value)
        return text


class TypoQuotes(BaseProcessor):
    """
    Replaces regular quotes with typographic ones.
    Supports any level nesting, but doesn't work well with minutes (1')
    and inches (1") within quotes, that kind of cases are ignored.
    """

    def __init__(self, *args, **kwargs):
        super(TypoQuotes, self).__init__(*args, **kwargs)

        # Odd and even levels: left, right
        self.loq, self.roq = self.typus.loq, self.typus.roq
        self.leq, self.req = self.typus.leq, self.typus.req

        # Replaces all quotes with `"`
        quotes = ''.join((LSQUO, RSQUO, LDQUO, RDQUO, DLQUO, LAQUO, RAQUO))
        self.re_normalize = re_compile(r'[{0}]'.format(quotes))

        # Matches quotes on the toppest level (with no quotes within)
        # and replaces with odd level quotes
        self.re_pairs = re_compile(
            # Word beginning or another _already_processed_ quote pair
            # or punctuation or html tag or escaped codeblock
            r'(?<!\w)'
            # Starts with quote
            r'(["\'])'
            r'(?!\s)'
            # Everything but quote inside
            r'([^\1]+?)'
            # Ends with same quote from the beginnig
            r'(?!\s)'
            r'\1'
            # Word end or processed quote or punctuation ot html tag or escaped
            # codeblock or inches or apostrophe
            r'(?!\w)')
        self.re_pairs_replace = r'{0}\2{1}'.format(self.loq, self.roq)

        # Matches to typo quotes
        self.re_typo_quotes = re_compile(r'({0}|{1}|[^{0}{1}]+)'
                                         .format(self.loq, self.roq))

    def __call__(self, func):
        @wraps(func)
        def inner(text, *args, **kwargs):
            # Normalizes edtior's quotes to double one
            normalized = self.re_normalize.sub('"', text)

            # Replaces normalized quotes with first level ones, starting
            # from inner pairs, moves to sides
            nested = -1
            while True:
                normalized, replaced = self.re_pairs.subn(
                    self.re_pairs_replace, normalized)
                if not replaced:
                    break
                nested += 1

            # Saves some cpu :)
            # Most cases are about just one level quoting
            if not nested:
                return func(normalized, *args, **kwargs)

            # At this point all quotes are of odd type, have to fix it
            fixed = self._fix_nesting(normalized)
            return func(fixed, *args, **kwargs)
        return inner

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


class Expressions(BaseProcessor):
    def __init__(self, *args, **kwargs):
        super(Expressions, self).__init__(*args, **kwargs)

        # Compiles expressions
        self.compiled_exprs = [
            (re_compile(*group[::2]), group[1])
            for name in self.typus.expressions.split()
            for group in getattr(self.typus, 'expr_' + name)()
        ]

    def __call__(self, func):
        @wraps(func)
        def inner(text, *args, **kwargs):
            # Applyies expressions
            for expr, repl in self.compiled_exprs:
                text = expr.sub(repl, text)
            text = func(text, *args, **kwargs)
            return text
        return inner
