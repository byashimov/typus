from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import *  # noqa
from functools import wraps
from itertools import count

from .utils import re_compile


class EscapeHtml(object):
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
    html_placeholder = '{{# codeblock{0} #}}'

    def __call__(self, typus):
        @wraps(typus)
        def inner(text, *args, **kwargs):
            escaped = text
            storage = []
            uid = count()
            for pattern in self.html_patterns:
                escaped = pattern.sub(
                    self._save_html(storage, uid), escaped)

            # Runs typus
            processed = typus(escaped, *args, **kwargs)
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

escape_html = EscapeHtml()
