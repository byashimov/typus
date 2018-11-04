# pylint: disable=unused-argument, method-hidden

from functools import update_wrapper

from .chars import NBSP, NNBSP
from .utils import re_compile

__all__ = ('TypusCore', )


class TypusCore:
    """
    This class runs :mod:`typus.processors` chained together.
    """

    processors = ()
    re_nbsp = re_compile('[{}{}]'.format(NBSP, NNBSP))

    def __init__(self):
        assert self.processors, 'Empty typus. Set processors'

        # Makes possible to decorate Typus.
        # updated=() skips __dict__ attribute
        update_wrapper(self, self.__class__, updated=())

        # Chains all processors into one single function
        self.procs = sum(p(self) for p in reversed(self.processors))

    def __call__(self, source: str, *, debug=False, **kwargs):
        text = source.strip()
        if not text:
            return ''

        # All the magic
        processed = self.procs.run(text, debug=debug, **kwargs)

        # Makes nbsp visible
        if debug:
            return self.re_nbsp.sub('_', processed)
        return processed
