from .base import TypusBase
from .expressions import EnRuExpressions
from .processors import QuotesProcessor
from .chars import LAQUO, RAQUO, DLQUO, LDQUO
from .decorators import escape_codeblocks


class Typus(EnRuExpressions, TypusBase):
    # Quotes: left odd, right odd, left even, right even
    loq, roq, leq, req = LAQUO, RAQUO, DLQUO, LDQUO
    processors = (QuotesProcessor, )


typus = escape_codeblocks(Typus())
