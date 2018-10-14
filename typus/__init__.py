# pylint: disable=invalid-name

from .core import TypusCore
from .processors import (
    EnQuotes,
    EnRuExpressions,
    EscapeHtml,
    EscapePhrases,
    RuQuotes,
)


class EnTypus(TypusCore):
    processors = (
        EscapePhrases,
        EscapeHtml,
        EnQuotes,
        EnRuExpressions,
    )


class RuTypus(TypusCore):
    processors = (
        EscapePhrases,
        EscapeHtml,
        RuQuotes,
        EnRuExpressions,
    )


en_typus, ru_typus = EnTypus(), RuTypus()
