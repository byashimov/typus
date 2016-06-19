# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import *  # noqa
from functools import update_wrapper

from .chars import NBSP
from .utils import re_compile


class TypusBase(object):
    """
    Typographer base
    """

    processors = ()
    expressions = ''

    def __init__(self):
        # Makes possible to decorate Typus.
        # updated=() skips __dic__ attribute
        update_wrapper(self, self.__class__, updated=())

        # Initiates processors
        self.inited_procs = [proc(self) for proc in self.processors]

        # Compiles expressions
        self.compiled_exprs = [
            (re_compile(pattern), replace)
            for name in self.expressions.split()
            for pattern, replace in getattr(self, 'expr_' + name)()
        ]

    def __call__(self, text, debug=False):
        # Applyies processors
        for proc in self.inited_procs:
            text = proc(text)

        # Applyies expressions
        for expr, repl in self.compiled_exprs:
            text = expr.sub(repl, text)

        # Makes nbsp visible
        if debug:
            return text.replace(NBSP, '_')
        return text
