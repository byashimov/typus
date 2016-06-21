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
        # Makes possible to decorate Typus.
        # updated=() skips __dic__ attribute
        update_wrapper(self, self.__class__, updated=())

        def chained(text, *args, **kwargs):
            return text

        for proc in (proc(self) for proc in reversed(self.processors)):
            chained = proc(chained)
        self.chained_procs = chained

    def __call__(self, text, debug=False, *args, **kwargs):
        text = text.strip()
        if not text or not self.chained_procs:
            return ''

        # All the magic
        text = self.chained_procs(text, *args, **kwargs)

        # Makes nbsp visible
        if debug:
            return text.replace(NBSP, '_')
        return text
