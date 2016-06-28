from .base import TypusBase
from .mixins import EnRuExpressions, RuQuotes
from .processors import EscapeHtml, EscapePhrases, TypoQuotes, Expressions


class Typus(RuQuotes, EnRuExpressions, TypusBase):
    processors = (EscapePhrases, EscapeHtml, TypoQuotes, Expressions)


typus = Typus()
