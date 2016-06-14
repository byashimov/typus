from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import *  # noqa
from functools import wraps
from itertools import count

from .utils import re_compile


class EscapeCodeblocks(object):
    """
    Extracts codeblocks and puts them back after
    typus processed.
    Warning: doesn't support nested code tags.
    """

    codeblocks_pattern = re_compile(r'(<pre>.*?</pre>|<code>.*?</code>)')
    codeblocks_placeholder = '{{# codeblock{0} #}}'

    def __call__(self, typus):
        @wraps(typus)
        def inner(text, *args, **kwargs):
            codeblocks, escaped = self._save_codeblocks(text)

            # Runs typus
            processed = typus(escaped, *args, **kwargs)
            if not codeblocks:
                return processed

            restored = self._restore_codeblocks(codeblocks, processed)
            return restored
        return inner

    def _save_codeblocks(self, text):
        codeblocks = {}
        counter = count()

        def replace(match):
            key = self.codeblocks_placeholder.format(next(counter))
            codeblocks[key] = match.group(0)
            return key

        text = self.codeblocks_pattern.sub(replace, text)
        return codeblocks, text

    def _restore_codeblocks(self, codeblocks, text):
        """
        This one could be static or even direclty placed in __call__
        but I need to know if it's called or not in mocked cases
        because coverage.py returnes summary report
        """
        for key, value in codeblocks.items():
            text = text.replace(key, value)
        return text

escape_codeblocks = EscapeCodeblocks()
