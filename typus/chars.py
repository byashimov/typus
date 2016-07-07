# coding: utf-8

from __future__ import unicode_literals

NBSP = '\u00A0'
WHSP = ' '
ANYSP = r'[{0}{1}]'.format(WHSP, NBSP)

NDASH = '–'
MDASH = '—'
MDASH_PAIR = NBSP + MDASH + WHSP

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
