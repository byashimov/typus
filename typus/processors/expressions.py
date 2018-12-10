import re
from functools import partial

from ..chars import *
from ..utils import RE_SCASE, doc_map, map_choices, re_choices, re_compile
from .base import BaseProcessor


class BaseExpressions(BaseProcessor):
    r"""
    Provides regular expressions support. Looks for ``expressions`` list
    attribute in Typus with expressions name, compiles and runs them on every
    Typus call.

    >>> from typus.core import TypusCore
    >>> from typus.processors import BaseExpressions
    ...
    >>> class MyExpressions(BaseExpressions):
    ...     expressions = ('bold_price', )  # no prefix `expr_`!
    ...     def expr_bold_price(self):
    ...         expr = (
    ...             (r'(\$\d+)', r'<b>\1</b>'),
    ...         )
    ...         return expr
    ...
    >>> class MyTypus(TypusCore):
    ...     processors = (MyExpressions, )
    ...
    >>> my_typus = MyTypus()  # `expr_bold_price` is compiled and stored
    >>> my_typus('Get now just for $1000!')
    'Get now just for <b>$1000</b>!'

    .. note::
        *Expression* is a pair of regex and replace strings. Regex strings are
        compiled with :func:`typus.utils.re_compile` with a bunch of flags:
        unicode, case-insensitive, etc. If that doesn't suit for you pass your
        own flags as a third member of the tuple: ``(regex, replace, re.I)``.
    """

    expressions = NotImplemented

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Compiles expressions
        self.compiled = tuple(
            partial(re_compile(*expr[::2]).sub, expr[1])
            for name in self.expressions
            for expr in getattr(self, 'expr_' + name)()
        )

    def run(self, text: str, **kwargs) -> str:
        for expression in self.compiled:
            text = expression(text)
        return self.run_other(text, **kwargs)


class EnRuExpressions(BaseExpressions):
    """
    This class holds most of Typus functionality for English and Russian
    languages.
    """

    expressions = (
        'spaces linebreaks apostrophe complex_symbols mdash primes '
        'digit_spaces pairs units ranges vulgar_fractions math ruble abbrs '
        'rep_positional_spaces del_positional_spaces'
    ).split()

    # Any unicode word
    words = r'[^\W\d_]'

    complex_symbols = {
        '...': '…',
        '<-': '←',
        '->': '→',
        '+-': '±',
        '+' + MINUS: '±',
        '<=': '≤',
        '>=': '≥',
        '/=': '≠',
        '==': '≡',
        '(r)': '®',
        '(c)': '©',
        '(p)': '℗',
        '(tm)': '™',
        '(sm)': '℠',
        'mA*h': 'mA•h',
        # cyrillic
        '(с)': '©',
        '(р)': '℗',
        '(тм)': '™',
        'мА*ч': 'мА•ч',
    }

    units = (
        'mm',
        'cm',
        'dm',
        'm',
        'km',
        'mg',
        'kg',
        'ml',
        'dpi',
        'mA•h',
        'мм',
        'см',
        'дм',
        'м',
        'км',
        'мг',
        'г',
        'кг',
        'т',
        'мл',
        'л',
        'мА•ч',
    )

    # This is for docs
    units_doc_map = {'1' + k: '1{}{}'.format(NBSP, k) for k in units}

    vulgar_fractions = {
        '1/2': '½',
        '1/3': '⅓',
        '1/4': '​¼',
        '1/5': '⅕',
        '1/6': '⅙',
        '1/8': '⅛',
        '2/3': '⅔',
        '2/5': '⅖',
        '3/4': '¾',
        '3/5': '⅗',
        '3/8': '⅜',
        '4/5': '⅘',
        '5/6': '⅚',
        '5/8': '⅝',
        '7/8': '⅞',
    }

    math = {
        '-': MINUS,
        '*xх': TIMES,
    }

    # No need to put >=, +-, etc, after expr_complex_symbols
    math_operators = r'[\-{0}\*xх{1}\+\=±≤≥≠÷\/]'.format(MINUS, TIMES)

    rep_positional_spaces = {
        # No need to put vulgar fractions in here because of expr_digit_spaces
        # which joins digits and words afterward
        'after': '←$€£%±{0}{1}©§¶№'.format(MINUS, TIMES),
        'both': '&≡≤≥≠',
        'before': '₽→' + MDASH,
    }

    del_positional_spaces = {
        'before': '®℗™℠:,.?!…',
    }

    ruble = (
        'руб',
        'р',
    )

    @staticmethod
    def expr_spaces():
        """
        Trims spaces at the beginning and end of the line and removes extra
        spaces within.

        >>> from typus import en_typus
        >>> en_typus('   foo bar  ')
        'foo bar'

        .. caution::
            Doesn't work correctly with nbsp (replaces with whitespace).
        """

        expr = (
            (r'{0}{{2,}}'.format(ANYSP), WHSP),
            (r'(?:^{0}+|{0}+$)'.format(ANYSP), ''),
        )
        return expr

    @staticmethod
    def expr_linebreaks():
        r"""
        Converts line breaks to unix-style and removes extra breaks
        if found more than two in a row.

        >>> from typus import en_typus
        >>> en_typus('foo\r\nbar\n\n\nbaz')
        'foo\nbar\n\nbaz'
        """

        expr = (
            (r'\r\n', '\n'),
            (r'\n{2,}', '\n' * 2),
        )
        return expr

    def expr_apostrophe(self):
        """
        Replaces single quote with apostrophe.

        >>> from typus import en_typus
        >>> en_typus("She'd, I'm, it's, don't, you're, he'll, 90's")
        'She’d, I’m, it’s, don’t, you’re, he’ll, 90’s'

        .. note::
            By the way it works with any omitted word. But then again, why not?
        """

        expr = (
            (r'(?<={0}|[0-9])\'(?={0})'.format(self.words), RSQUO),
        )
        return expr

    @doc_map(complex_symbols)
    def expr_complex_symbols(self):
        """
        Replaces complex symbols with Unicode characters. Doesn't care
        about case-sensitivity and handles Cyrillic-Latin twins
        like ``c`` and ``с``.

        >>> from typus import en_typus
        >>> en_typus('(c)(с)(C)(r)(R)...')
        '©©©®®…'
        """

        expr = (
            map_choices(self.complex_symbols),
        )
        return expr

    @staticmethod
    def expr_mdash():
        """
        Replaces dash with mdash.

        >>> from typus import en_typus
        >>> en_typus('foo -- bar')  # adds non-breaking space after `foo`
        'foo\u202f—\u2009bar'
        """

        expr = (
            # Double dash guarantees to be replaced with mdash
            (r'{0}--{0}'.format(WHSP), MDASH_PAIR),

            # Dash can be between anything except digits
            # because in that case it's not obvious
            (r'{0}+[\-|{1}]{0}+(?!\d\b)'.format(ANYSP, NDASH), MDASH_PAIR),

            # Same but backwards
            # It joins non-digit with digit or word
            (r'(\b\D+){0}+[\-|{1}]{0}+'.format(ANYSP, NDASH),
             r'\1{0}'.format(MDASH_PAIR)),

            # Line beginning adds nbsp after dash
            (r'^\-{{1,2}}{0}+'.format(ANYSP),
             r'{0}{1}'.format(MDASH, NBSP)),

            # Also mdash can be at the end of the line in poems
            (r'{0}+\-{{1,2}}{0}*(?=$|<br/?>)'.format(ANYSP),
             r'{0}{1}'.format(NBSP, MDASH)),

            # Special case with leading comma
            (',' + MDASH_PAIR, f',{MDASH}{THNSP}'),
        )
        return expr

    @staticmethod
    def expr_primes():
        r"""
        Replaces quotes with prime after digits.

        >>> from typus import en_typus
        >>> en_typus('3\' 5" long')
        '3′ 5″ long'

        .. caution::
            Won't break ``"4"``, but fails with ``" 4"``.
        """

        expr = (
            (r'(^|{0})(\d+)\''.format(ANYSP), r'\1\2' + SPRIME),
            (r'(^|{0})(\d+)"'.format(ANYSP), r'\1\2' + DPRIME),
        )
        return expr

    def expr_digit_spaces(self):
        """
        Replaces whitespace with non-breaking space after 4 (and less)
        length digits if word or digit without comma or math operators
        found afterwards:
        3 apples
        40 000 bucks
        400 + 3
        Skips:
        4000 bucks
        40 000,00 bucks
        """

        expr = (
            (r'\b(\d{{1,3}}){0}(?=[0-9]+\b|{1}|{2})'
             .format(WHSP, self.words, self.math_operators), r'\1' + NBSP),
        )
        return expr

    def expr_pairs(self):
        """
        Replaces whitespace with non-breaking space after 1-2 length words.
        """

        expr = (
            # Unions, units and all that small staff
            (r'\b({1}{{1,2}}){0}+'.format(WHSP, self.words), r'\1' + NBSP),
            # Fixes previous with leading dash, ellipsis or apostrophe
            (r'([-…’]{1}{{1,2}}){0}'.format(NBSP, self.words), r'\1' + WHSP),
        )
        return expr

    @doc_map(units_doc_map)
    def expr_units(self):
        """
        Puts narrow non-breaking space between digits and units.
        Case sensitive.

        >>> from typus import en_typus
        >>> en_typus('1mm', debug=True), en_typus('1mm')
        ('1_mm', '1 mm')
        """

        expr = (
            (r'\b(\d+){0}*{1}\b'.format(WHSP, re_choices(self.units)),
             r'\1{0}\2'.format(NBSP), RE_SCASE),
        )
        return expr

    def expr_ranges(self):
        """
        Replaces dash with ndash in ranges.
        Supports float and negative values.
        Tries to not mess with minus: skips if any math operator or word
        was found after dash: 3-2=1, 24-pin.
        **NOTE**: _range_ should not have spaces between dash: `2-3` and
        left side should be less than right side.
        """

        def ufloat(string):
            return float(string.replace(',', '.'))

        def replace(match):
            left, dash, right = match.groups()
            if ufloat(left) < ufloat(right):
                dash = NDASH
            return '{0}{1}{2}'.format(left, dash, right)

        expr = (
            (r'(-?(?:[0-9]+[\.,][0-9]+|[0-9]+))(-)'
             r'([0-9]+[\.,][0-9]+|[0-9]+)'
             r'(?!{0}*{1}|{2})'
             .format(ANYSP, self.math_operators, self.words),
             replace),
        )
        return expr

    @doc_map(vulgar_fractions)
    def expr_vulgar_fractions(self):
        """
        Replaces vulgar fractions with appropriate unicode characters.

        >>> from typus import en_typus
        >>> en_typus('1/2')
        '½'
        """

        expr = (
            # \b to excludes digits which are not on map, like `11/22`
            map_choices(self.vulgar_fractions, r'\b({0})\b'),
        )
        return expr

    @doc_map(math)
    def expr_math(self):
        """
        Puts minus and multiplication symbols between pair and before
        single digits.

        >>> from typus import en_typus
        >>> en_typus('3 - 3 = 0')
        '3 − 3 = 0'
        >>> en_typus('-3 degrees')
        '−3 degrees'
        >>> en_typus('3 x 3 = 9')
        '3 × 3 = 9'
        >>> en_typus('x3 better!')
        '×3 better!'
        """

        expr = (
            (r'(^|{0}|\d)[{1}]({0}*\d)'.format(ANYSP, re.escape(x)),
             r'\1{0}\2'.format(y)) for x, y in self.math.items()
        )
        return expr

    def expr_abbrs(self):
        """
        Adds narrow non-breaking space and replaces whitespaces between
        shorten words.
        """

        expr = (
            (r'\b({1}\.){0}*({1}\.)'.format(ANYSP, self.words),
             r'\1{0}\2'.format(NNBSP)),
            (r'\b({1}\.){0}*(?={1})'.format(WHSP, self.words),
             r'\1{0}'.format(NBSP)),
        )
        return expr

    def expr_ruble(self):
        """
        Replaces `руб` and `р` (with or without dot) after digits
        with ruble symbol. Case sensitive.

        >>> from typus import en_typus
        >>> en_typus('1000 р.')
        '1000 ₽'

        .. caution::

            Drops the dot at the end of sentence if match found in there.
        """

        choices = re_choices(self.ruble, r'(?:{0})')
        expr = (
            (r'(\d){0}*{1}\b\.?'.format(ANYSP, choices),
             r'\1{0}₽'.format(NBSP), RE_SCASE),  # case matters
        )
        return expr

    @staticmethod
    def _positional_spaces(data, find, replace):
        """
        Helper method for `rep_positional_spaces` and `del_positional_spaces`
        expressions.
        """

        both = data.get('both', '')
        before = re.escape(data.get('before', '') + both)
        after = re.escape(data.get('after', '') + both)
        if before:
            yield r'{0}+(?=[{1}])'.format(find, before), replace
        if after:
            yield r'(?<=[{1}]){0}+'.format(find, after), replace

    @doc_map(rep_positional_spaces, keys='Direction', values='Characters')
    def expr_rep_positional_spaces(self):
        """
        Replaces whitespaces after and before certain symbols
        with non-breaking space.
        """

        expr = self._positional_spaces(self.rep_positional_spaces, WHSP, NBSP)
        return tuple(expr)

    @doc_map(del_positional_spaces, keys='Direction', values='Characters')
    def expr_del_positional_spaces(self):
        """
        Removes spaces before and after certain symbols.
        """

        expr = self._positional_spaces(self.del_positional_spaces, ANYSP, '')
        return tuple(expr)
