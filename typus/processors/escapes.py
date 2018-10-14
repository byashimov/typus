from abc import abstractmethod
from itertools import count

from ..utils import re_compile
from .base import BaseProcessor


class BaseEscapeProcessor(BaseProcessor):
    def run(self, text: str, **kwargs) -> str:
        storage = []
        counter = count()
        escaped = self._save_values(text, storage, counter, **kwargs)

        # Runs typus
        processed = self.run_other(escaped, **kwargs)
        if not storage:
            return processed

        restored = self._restore_values(processed, storage)
        return restored

    @abstractmethod
    def _save_values(self, *args, **kwargs):
        pass  # pragma: nocover

    @staticmethod
    def _restore_values(text, storage):
        """
        Puts data into the text in reversed order.
        It's important to loop over and restore text step by step
        because some 'stored' chunks may contain keys to other ones.
        """
        for key, value in reversed(storage):
            text = text.replace(key, value)
        return text


class EscapePhrases(BaseEscapeProcessor):
    """
    Escapes phrases which should never be processed.

    >>> from typus import en_typus
    >>> en_typus('Typus turns `(c)` into "(c)"', escape_phrases=['`(c)`'])
    'Typus turns `(c)` into “©”'

    Also there is a little helper :func:`typus.utils.splinter` which should
    help you to split string into the phrases.
    """

    placeholder = '{{#phrase{0}#}}'

    def _save_values(
            self, text, storage, counter, escape_phrases=(), **kwargs):
        for phrase in escape_phrases:
            if not phrase.strip():
                continue
            key = self.placeholder.format(next(counter))
            text = text.replace(phrase, key)
            storage.append((key, phrase))
        return text


class EscapeHtml(BaseEscapeProcessor):
    """
    Extracts html tags and puts them back after.

    >>> from typus import en_typus
    >>> en_typus('Typus turns <code>(c)</code> into "(c)"')
    'Typus turns <code>(c)</code> into “©”'

    .. caution::
        Doesn't support nested ``<code>`` tags.
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

    def _save_values(self, text, storage, counter, **kwargs):
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
