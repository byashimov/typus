"""
Tests expressions one by one.
Some of them may return different results depending on which was
applied earlier, so order matters. But that also means it's important
to be sure they don't affect each other more than expected. This case
tests every expression as if it was the only one to apply.
"""
import pytest

from typus.chars import *
from typus.core import TypusCore
from typus.processors import EnRuExpressions


@pytest.fixture(name='factory')
def get_factory():
    def factory(*exps):
        class MyExpressions(EnRuExpressions):
            expressions = exps

        class Typus(TypusCore):
            processors = (MyExpressions, )
        return Typus()
    return factory


@pytest.mark.parametrize('source, expected', (
    ('110 р', f'110{NBSP}₽'),
    ('111 р.', f'111{NBSP}₽'),
    ('112 руб', f'112{NBSP}₽'),
    ('113 руб.', f'113{NBSP}₽'),
    # With comma
    ('114,00 р', f'114,00{NBSP}₽'),
    ('115.00 р', f'115.00{NBSP}₽'),
    # Ignores
    ('116 рубчиков', '116 рубчиков'),
    ('117 ру', '117 ру'),
    # Case sensivity
    ('117 Р', '117 Р'),
))
def test_ruble(factory, source, expected):
    typus = factory('ruble')
    assert expected == typus(source)


@pytest.mark.parametrize('source, expected', (
    ('foo{}bar'.format(' ' * 30), 'foo bar'),
))
def test_spaces(factory, source, expected):
    typus = factory('spaces')
    assert expected == typus(source)


@pytest.mark.parametrize('source, expected', (
    ('a\nb', 'a\nb'),
    ('a\r\nb', 'a\nb'),
    ('a{0}b'.format('\n' * 5), 'a\n\nb'),
    ('a\n\n\r\nb', 'a\n\nb'),
))
def test_linebreaks(factory, source, expected):
    typus = factory('linebreaks')
    assert expected == typus(source)


@pytest.mark.parametrize('source, expected', (
    ("She'd", f'She{RSQUO}d'),
    ("I'm", f'I{RSQUO}m'),
    ("it's", f'it{RSQUO}s'),
    ("don't", f'don{RSQUO}t'),
    ("you're", f'you{RSQUO}re'),
    ("he'll", f'he{RSQUO}ll'),
    ("90's", f'90{RSQUO}s'),
    ("Карло's", f'Карло{RSQUO}s'),
))
def test_apostrophe(factory, source, expected):
    typus = factory('apostrophe')
    assert expected == typus(source)


@pytest.mark.parametrize('source, expected', (
    ('--', '--'),
    (', - foo', f',{MDASH_PAIR}foo'),
    ('foo - foo', f'foo{MDASH_PAIR}foo'),
    # if line begins, adds nbsp after mdash
    ('-- foo', f'{MDASH}{NBSP}foo'),
    # if line ends, adds nbsp before mdash
    ('foo --', f'foo{NBSP}{MDASH}'),
    ('foo -- bar', f'foo{MDASH_PAIR}bar'),
    (', -- foo', f',{MDASH_PAIR}foo'),
    # Python markdown replaces dash with ndash, don't know why
    (f'foo {NDASH} foo', f'foo{MDASH_PAIR}foo'),
    ('foo - "11" 00', f'foo{MDASH_PAIR}"11" 00'),
    ('2 - 2foo', f'2{MDASH_PAIR}2foo'),
    ('2 - 2', '2 - 2'),  # Doesn't clash with minus
))
def test_mdash(factory, source, expected):
    typus = factory('mdash')
    assert expected == typus(source)


@pytest.mark.parametrize('source, expected', (
    ('4\'', '4' + SPRIME),
    ('4"', '4' + DPRIME),
    ('" 22"', '" 22' + DPRIME),
    ('"4"', '"4"'),
))
def test_primes(factory, source, expected):
    typus = factory('primes')
    assert expected == typus(source)


@pytest.mark.parametrize('source, expected', (
    ('555-55-55', f'555{NDASH}55{NDASH}55'),
    ('55-555-55', f'55{NDASH}555{NDASH}55'),
    ('55-555', '55-555'),  # skips
))
def test_phones(factory, source, expected):
    typus = factory('phones')
    assert expected == typus(source)


@pytest.mark.parametrize('source, expected', (
    ('4444444 fooo', '4444444 fooo'),
    ('444 foo', f'444{NBSP}foo'),
    ('444 +', f'444{NBSP}+'),
    ('444 4444 bucks', f'444{NBSP}4444 bucks'),
    ('444 -', f'444{NBSP}-'),
    ('4444444 foo', '4444444 foo'),
))
def test_digit_spaces(factory, source, expected):
    typus = factory('digit_spaces')
    assert expected == typus(source)


@pytest.mark.parametrize('source, expected', (
    ('aaa aaa', 'aaa aaa'),
    ('aaa-aa aa', 'aaa-aa aa'),  # important check -- dash and 2 letters
    ('aaa aa', 'aaa aa'),
    ('I’ll check', 'I’ll check'),
    ('a aa a', f'a{NBSP}aa{NBSP}a'),
    ('aaa 2a', 'aaa 2a')  # letters only, no digits,
))
def test_pairs(factory, source, expected):
    typus = factory('pairs')
    assert expected == typus(source)


@pytest.mark.parametrize('source, expected', (
    # Latin
    ('1mm', f'1{NBSP}mm'),
    ('1cm', f'1{NBSP}cm'),
    ('1dm', f'1{NBSP}dm'),
    ('1m', f'1{NBSP}m'),
    ('1km', f'1{NBSP}km'),
    ('1mg', f'1{NBSP}mg'),
    ('1kg', f'1{NBSP}kg'),
    ('1ml', f'1{NBSP}ml'),
    ('1mA•h', f'1{NBSP}mA•h'),
    ('1dpi', f'1{NBSP}dpi'),
    # Cyrillic
    ('1мм', f'1{NBSP}мм'),
    ('1см', f'1{NBSP}см'),
    ('1дм', f'1{NBSP}дм'),
    ('1м', f'1{NBSP}м'),
    ('1км', f'1{NBSP}км'),
    ('1мг', f'1{NBSP}мг'),
    ('1г', f'1{NBSP}г'),
    ('1кг', f'1{NBSP}кг'),
    ('1мл', f'1{NBSP}мл'),
    ('1л', f'1{NBSP}л'),
    ('1т', f'1{NBSP}т'),
    ('1мА•ч', f'1{NBSP}мА•ч'),
    # Skips
    ('1foobar', '1foobar'),
    # Exceptions
    ('3g', '3g'),  # 4G lte
    ('3d', '3d'),  # 3D movie
    ('2nd', '2nd'),  # floor
    ('3rd', '3rd'),  # floor
    ('4th', '4th'),  # floor
    ('1px', '1px'),
    ('1000A', '1000A'),
    # Case sensivity
    ('1000ML', '1000ML'),
))
def test_units(factory, source, expected):
    typus = factory('units')
    assert expected == typus(source)


@pytest.mark.parametrize('source, expected', (
    ('25-foo', '25-foo'),
    ('2-3', f'2{NDASH}3'),
    ('2,5-3', f'2,5{NDASH}3'),
    ('0.5-3', f'0.5{NDASH}3'),

    ('2-3 foo', f'2{NDASH}3 foo'),
    ('(15-20 items)', f'(15{NDASH}20 items)'),

    # Float
    ('0,5-3', f'0,5{NDASH}3'),
    ('-0,5-3', f'-0,5{NDASH}3'),
    ('-5.5-3', f'-5.5{NDASH}3'),
    ('-5,5-3', f'-5,5{NDASH}3'),
    ('-5,5-3.5', f'-5,5{NDASH}3.5'),

    # Skips
    ('2 - 3', '2 - 3'),
    ('2-3 x 4', '2-3 x 4'),
    ('2-3 * 4', '2-3 * 4'),
    ('2-3 - 4', '2-3 - 4'),

    # Left is less than or equal to right
    ('3-2', '3-2'),
    ('3-3', '3-3'),
))
def test_ranges(factory, source, expected):
    typus = factory('ranges')
    assert expected == typus(source)


@pytest.mark.parametrize('source, expected', (
    ('(C)', '©'),  # Case insensitive test
    ('...', '…'),
    ('<-', '←'),
    ('->', '→'),
    ('+-', '±'),
    ('+' + MINUS, '±'),
    ('<=', '≤'),
    ('>=', '≥'),
    ('/=', '≠'),
    ('==', '≡'),
    ('(r)', '®'),
    ('(c)', '©'),
    ('(p)', '℗'),
    ('(tm)', '™'),
    ('(sm)', '℠'),
    ('mA*h', 'mA•h'),
    # cyrillic
    ('(с)', '©'),
    ('(р)', '℗'),
    ('(тм)', '™',),
    ('мА*ч', 'мА•ч'),
))
def test_complex_symbols(factory, source, expected):
    typus = factory('complex_symbols')
    assert expected == typus(source)


@pytest.mark.parametrize('source, expected', (
    ('1/2', '½'),
    ('1/3', '⅓'),
    ('1/4', '​¼'),
    ('1/5', '⅕'),
    ('1/6', '⅙'),
    ('1/8', '⅛'),
    ('2/3', '⅔'),
    ('2/5', '⅖'),
    ('3/4', '¾'),
    ('3/5', '⅗'),
    ('3/8', '⅜'),
    ('4/5', '⅘'),
    ('5/6', '⅚'),
    ('5/8', '⅝'),
    ('7/8', '⅞'),
    # False positive
    ('11/22', '11/22'),
))
def test_vulgar_fractions(factory, source, expected):
    typus = factory('vulgar_fractions')
    assert expected == typus(source)


@pytest.mark.parametrize('source, expected', (
    ('-', MINUS),
    ('*', TIMES),
    ('x', TIMES),
    ('х', TIMES),
))
def test_math(factory, source, expected):
    typus = factory('math')
    # -3, 3-3, 3 - 3, x - 3
    assert typus(source + '3') == expected + '3'
    assert typus(f'word{source} 3') == f'word{source} 3'
    assert typus(f'3{source}3') == f'3{expected}3'
    assert typus(f'3 {source} 3') == f'3 {expected} 3'
    assert typus(f'x {source} 3') == f'x {expected} 3'


@pytest.mark.parametrize('source, expected', (
    ('т. д.', f'т.{NNBSP}д.'),
    ('т.д.', f'т.{NNBSP}д.'),
    ('т.п.', f'т.{NNBSP}п.'),
    ('т. ч.', f'т.{NNBSP}ч.'),
    ('т.е.', f'т.{NNBSP}е.'),
    ('Пушкин А.С.', f'Пушкин А.{NNBSP}С.'),
    ('А.С. Пушкин', f'А.{NNBSP}С.{NBSP}Пушкин'),
))
def test_abbrs(factory, source, expected):
    typus = factory('abbrs')
    assert expected == typus(source)


@pytest.mark.parametrize('char', f'←$€£%±{MINUS}{TIMES}©§¶№')
def test_rep_positional_spaces_after(factory, char):
    typus = factory('rep_positional_spaces')
    assert typus(f'foo {char} bar') == f'foo {char}{NBSP}bar'


@pytest.mark.parametrize('char', '&≡≤≥≠')
def test_rep_positional_spaces_both(factory, char):
    typus = factory('rep_positional_spaces')
    assert typus(f'foo {char} bar') == f'foo{NBSP}{char}{NBSP}bar'


@pytest.mark.parametrize('char', '₽→' + MDASH)
def test_rep_positional_spaces_before(factory, char):
    typus = factory('rep_positional_spaces')
    assert typus(f'foo {char} bar') == f'foo{NBSP}{char} bar'


@pytest.mark.parametrize('char', '®℗™℠:,.?!…')
def test_rdel_positional_spaces_before(factory, char):
    typus = factory('del_positional_spaces')
    assert typus(f'foo {char} bar') == f'foo{char} bar'
