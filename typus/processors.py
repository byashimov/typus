from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import *  # noqa
from functools import update_wrapper, wraps
from itertools import count, cycle

from .chars import DLQUO, LAQUO, LDQUO, LSQUO, RAQUO, RDQUO, RSQUO
from .utils import re_compile

def mock_processor(text, *args, **kwargs):
    return text


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

    def __radd__(self, other):
        return self(other or mock_processor)


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
    skiptags = 'head|iframe|pre|code|script|style|video|audio|canvas'
    patterns = (
        re_compile(r'(<)({0})(.*?>.*?</\2>)'.format(skiptags)),
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
    Replaces regular quotes with typographic.
    Supports any level nesting, but doesn't work well with minutes (1')
    and inches (1") within quotes, that kind of cases are ignored.
    """

    def __init__(self, *args, **kwargs):
        super(TypoQuotes, self).__init__(*args, **kwargs)

        # Odd and even levels: left, right
        self.loq, self.roq = self.typus.loq, self.typus.roq
        self.leq, self.req = self.typus.leq, self.typus.req

        # Pairs of odd and even quotes. Already *switched* in one dimension.
        # See :meth:`switch_nested` for more help.
        self.switch = (self.loq + self.req, self.leq + self.roq)

        # Replaces all quotes with `"`
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

    def __call__(self, func):
        @wraps(self, updated=())
        def inner(text, *args, **kwargs):
            # Normalizes editor's quotes to double one
            normalized = self.re_normalize.sub('"', text)

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
                return func(normalized, *args, **kwargs)

            # At this point all quotes are of odd type, have to fix it
            switched = self.switch_nested(normalized)
            return func(switched, *args, **kwargs)
        return inner

    def switch_nested(self, text):
        """
        Switches nested quotes to *other* type.
        This function stored in a separate method to make possible it to mock
        in tests to make sure it doesn't called without special need.
        """

        # Stores a cycled pairs of possible quotes. Every other loop it's
        # switched to provide *next* type of a given quote
        quotes = cycle(self.switch)

        def replace(match):
            # Since only odd quotes are matched, comparison is the way to
            # choose whether it's left or right one of type should be returned.
            # As the first quote is the left one, makes negative equal which
            # return false, i.e. zero index
            return next(quotes)[match.group() != self.loq]
        return self.re_nested.sub(replace, text)


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
