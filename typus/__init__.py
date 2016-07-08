from .core import TypusCore
from .mixins import EnQuotes, EnRuExpressions, RuQuotes
from .processors import EscapeHtml, EscapePhrases, Expressions, TypoQuotes


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
