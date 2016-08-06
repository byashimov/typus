from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import *  # noqa
from functools import update_wrapper

from .chars import NBSP

__all__ = ('TypusCore', )


class TypusCore(object):
    """
    Typographer base
    """

    processors = ()
    expressions = ()

    def __init__(self):
        assert self.processors

        # Makes possible to decorate Typus.
        # updated=() skips __dic__ attribute
        update_wrapper(self, self.__class__, updated=())

        # Chains all processors into one single function
        self.process = sum(p(self) for p in reversed(self.processors))

    def __call__(self, text, debug=False, *args, **kwargs):
        text = text.strip()
        if not text:
            return ''

        # All the magic
        text = self.process(text, *args, **kwargs)

        # Makes nbsp visible
        if debug:
            return text.replace(NBSP, '_')
        return text
