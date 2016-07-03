# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import *  # noqa
from functools import update_wrapper, wraps
from itertools import count, cycle

from .chars import LSQUO, RSQUO, LDQUO, RDQUO, DLQUO, LAQUO, RAQUO
from .utils import re_compile


class BaseProcessor(object):
    """
    Processors are simple python decorators, except they are initiated
    and stored within Typus instance.
    """

    def __init__(self, typus):
        # Makes possible to decorate processor
        update_wrapper(self, self.__class__, updated=())

        # Stores Typus to access it's configuration
        self.typus = typus

    def __call__(self, typus):
        raise NotImplementedError


class EscapePhrases(BaseProcessor):
    """
    Escapes phrases which should never be processed.
    """

    placeholder = '{{#phrase{0}#}}'

    def __call__(self, func):
        @wraps(self, updated=())
        def inner(text, *args, **kwargs):
            storage = []
            counter = count()
            escaped = self.save_values(text, storage, counter, **kwargs)

            # Runs typus
            processed = func(escaped, *args, **kwargs)
            if not storage:
                return processed

            restored = self.restore_values(processed, storage, **kwargs)
            return restored
        return inner

    def save_values(self, text, storage, counter, escape_phrases=(), **kwargs):
        for phrase in escape_phrases:
            if not phrase.strip():
                continue
            key = self.placeholder.format(next(counter))
            text = text.replace(phrase, key)
            storage.append((key, phrase))
        return text

    def restore_values(self, text, storage, **kwargs):
        """
        Puts data to the text in reversed order.
        It's important to loop over and restore text step by step
        because some 'stored' chunks may contain keys to other ones.
        """
        for key, value in reversed(storage):
            text = text.replace(key, value)
        return text


class EscapeHtml(EscapePhrases):
    """
    Extracts html tags and puts them back after
    typus processed.
    Warning: doesn't support nested code tags.
    """

    placeholder = '{{#html{0}#}}'
    patterns = (
        re_compile(r'(<)(head|iframe|pre|code|script|style)(.*?>.*?</\2>)'),
        # Doctype, xml, closing tag, any tag
        re_compile(r'(<[\!\?/]?[a-z]+.*?>)'),
        # Comments
        re_compile(r'(<\!\-\-.*?\-\->)'),
    )

    def save_values(self, text, storage, counter, **kwargs):
        for pattern in self.patterns:
            text = pattern.sub(self._replace(storage, counter), text)
        return text

    def _replace(self, storage, counter):
        def inner(match):
            key = self.placeholder.format(next(counter))
            html = ''.join(match.groups())
            storage.append((key, html))
            return key
        return inner


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

        # Matches nested quotes (with no quotes within)
        # and replaces with odd level quotes
        self.re_pairs = re_compile(
            # No words before
            r'(?<!\w)'
            # Starts with quote
            r'(["\'])'
            r'(?!\s)'
            # Everything but quote inside
            r'([^\1]+?)'
            r'(?!\s)'
            # Ends with same quote from the beginning
            r'\1'
            # No words afterwards
            r'(?!\w)'
        )
        self.re_pairs_replace = r'{0}\2{1}'.format(self.loq, self.roq)

        # Matches to typo quotes
        self.re_typo_quotes = re_compile(r'({0}|{1}|[^{0}{1}]+)'
                                         .format(self.loq, self.roq))

    def __call__(self, func):
        @wraps(self, updated=())
        def inner(text, *args, **kwargs):
            # Normalizes editor's quotes to double one
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
            fixed = self.fix_nesting(normalized)
            return func(fixed, *args, **kwargs)
        return inner

    def fix_nesting(self, normalized):
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
    """
    Provides expressions support.
    """

    def __init__(self, *args, **kwargs):
        super(Expressions, self).__init__(*args, **kwargs)

        # Compiles expressions
        self.compiled_exprs = [
            (re_compile(*group[::2]), group[1])
            for name in self.typus.expressions
            for group in getattr(self.typus, 'expr_' + name)()
        ]

    def __call__(self, func):
        @wraps(self, updated=())
        def inner(text, *args, **kwargs):
            # Applies expressions
            for expr, repl in self.compiled_exprs:
                text = expr.sub(repl, text)
            text = func(text, *args, **kwargs)
            return text
        return inner
