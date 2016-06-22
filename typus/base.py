# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import *  # noqa
from functools import update_wrapper

from .chars import NBSP


class TypusBase(object):
    """
    Typographer base
    """

    processors = ()
    expressions = ''

    def __init__(self):
        assert self.processors

        # Makes possible to decorate Typus.
        # updated=() skips __dic__ attribute
        update_wrapper(self, self.__class__, updated=())

        def tail(text, *args, **kwargs):
            """
            Tail function to close the chain of processors
            """
            return text

        # Makes chain of processors by passing one to next one
        processors = (p(self) for p in reversed(self.processors))
        for proc in processors:
            tail = proc(tail)

        self.chained_procs = tail

    def __call__(self, text, debug=False, *args, **kwargs):
        text = text.strip()
        if not text:
            return ''

        # All the magic
        text = self.chained_procs(text, *args, **kwargs)

        # Makes nbsp visible
        if debug:
            return text.replace(NBSP, '_')
        return text
