__all__ = (
    'ANYSP',
    'DLQUO',
    'DPRIME',
    'LAQUO',
    'LDQUO',
    'LSQUO',
    'MDASH',
    'MDASH_PAIR',
    'MINUS',
    'NBSP',
    'NDASH',
    'NNBSP',
    'RAQUO',
    'RDQUO',
    'RSQUO',
    'SPRIME',
    'THNSP',
    'TIMES',
    'WHSP',
)

NBSP = '\u00A0'
NNBSP = '\u202F'
THNSP = '\u2009'
WHSP = ' '
ANYSP = r'[{}{}{}{}]'.format(WHSP, NBSP, NNBSP, THNSP)

NDASH = '–'
MDASH = '—'
MDASH_PAIR = NNBSP + MDASH + THNSP
HYPHEN = ''

MINUS = '−'
TIMES = '×'

LSQUO = '‘'  # left curly quote mark
RSQUO = '’'  # right curly quote mark/apostrophe
LDQUO = '“'  # left curly quote marks
RDQUO = '”'  # right curly quote marks
DLQUO = '„'  # double low curly quote mark
LAQUO = '«'  # left angle quote marks
RAQUO = '»'  # right angle quote marks

SPRIME = '′'
DPRIME = '″'
