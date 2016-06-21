from .base import TypusBase
from .expressions import EnRuExpressions
from .processors import EscapeHtml, TypoQuotes, Expressions
from .chars import LAQUO, RAQUO, DLQUO, LDQUO


class Typus(EnRuExpressions, TypusBase):
    # Quotes: left odd, right odd, left even, right even
    loq, roq, leq, req = LAQUO, RAQUO, DLQUO, LDQUO
    processors = (EscapeHtml, TypoQuotes, Expressions)


typus = Typus()
