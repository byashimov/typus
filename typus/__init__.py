from .core import TypusCore
from .mixins import EnRuExpressions, EnQuotes, RuQuotes
from .processors import EscapeHtml, EscapePhrases, TypoQuotes, Expressions


class BaseTypus(EnRuExpressions, TypusCore):
    processors = (EscapePhrases, EscapeHtml, TypoQuotes, Expressions)


class EnTypus(EnQuotes, BaseTypus):
    """
    TODO:
    """


class RuTypus(RuQuotes, BaseTypus):
    """
    TODO:
    """


en_typus, ru_typus = EnTypus(), RuTypus()
