import pytest

from typus import en_typus, ru_typus
from typus.chars import *

QUOTES = (
    ''.join((LAQUO, RAQUO, DLQUO, LDQUO)),
    ''.join((LDQUO, RDQUO, LSQUO, RSQUO)),
)
TYPUSES = (
    (ru_typus, {}),
    (en_typus, str.maketrans(*QUOTES)),
)


@pytest.fixture(name='assert_typus', scope='module', params=TYPUSES)
def get_assert_typus(request):
    typus, charmap = request.param

    def assert_typus(source, expected):
        assert typus(source) == expected.translate(charmap)
    return assert_typus


def test_debug():
    assert ru_typus('1m', debug=True) == '1_m'


@pytest.mark.parametrize('source, expected', (
    ('00 "11" 00', '00 «11» 00'),
    # clashes with digit_spaces
    (
        '''00" "11 '22' 11"? "11 '22 "33 33?"' 11" 00 "11 '22' 11" 0"''',
        f'00{DPRIME} «11 „22“ 11»? «11 „22 «33{NBSP}33?»“ 11» '
        f'00 «11 „22“ 11» 0{DPRIME}'
    ),
))
def test_quotes(assert_typus, source, expected):
    assert_typus(source, expected)


@pytest.mark.parametrize('source, expected', (
    ('--', '--'),
    ('foo - foo', f'foo{MDASH_PAIR}foo'),
    # Leading comma case
    (', - foo', f',{MDASH}{THNSP}foo'),
    (', -- foo', f',{MDASH}{THNSP}foo'),
    # if line begins, adds nbsp after mdash
    ('-- foo', f'{MDASH}{NBSP}foo'),
    # if line ends, adds nbsp before mdash
    ('foo --', f'foo{NBSP}{MDASH}'),
    ('foo -- bar', f'foo{MDASH_PAIR}bar'),
    # Python markdown replaces dash with ndash, don't know why
    (f'foo {NDASH} foo', f'foo{MDASH_PAIR}foo'),

    # This one for ru_typus
    ('foo - "11" 00', f'foo{MDASH_PAIR}«11» 00'),
    ('2 - 2foo', f'2{MDASH_PAIR}2foo'),  # no units clash
    ('2 - 2', f'2{NBSP}{MINUS}{NBSP}2'),  # + minus
    ('Winnie-the-Pooh', 'Winnie-the-Pooh'),
))
def test_mdash(assert_typus, source, expected):
    assert_typus(source, expected)


@pytest.mark.parametrize('source, expected', (
    ('"4"', '«4»'),
    ('4\'', '4' + SPRIME),
    ('4"', '4' + DPRIME),
    ('" 22"', '" 22' + DPRIME),
))
def test_primes(assert_typus, source, expected):
    assert_typus(source, expected)


@pytest.mark.parametrize('source, expected', (
    ('25-foo', '25-foo'),
    ('2-3', f'2{NDASH}3'),
    ('2,5-3', f'2,5{NDASH}3'),
    ('0.5-3', f'0.5{NDASH}3'),
    ('2-3 foo', f'2{NDASH}3{NBSP}foo'),  # + ranges
    ('(15-20 items)', f'(15{NDASH}20{NBSP}items)'),

    # Float
    ('0,5-3', f'0,5{NDASH}3'),
    ('-0,5-3', f'{MINUS}0,5{NDASH}3'),
    ('-5.5-3', f'{MINUS}5.5{NDASH}3'),
    ('-5,5-3', f'{MINUS}5,5{NDASH}3'),
    ('-5,5-3.5', f'{MINUS}5,5{NDASH}3.5'),
    ('2 - 3', f'2{NBSP}{MINUS}{NBSP}3'),
    ('2-3 x 4', f'2{MINUS}3{NBSP}{TIMES}{NBSP}4'),
    ('2-3 * 4', f'2{MINUS}3{NBSP}{TIMES}{NBSP}4'),
    ('2-3 - 4', f'2{MINUS}3{NBSP}{MINUS}{NBSP}4'),
))
def test_ranges(assert_typus, source, expected):
    assert_typus(source, expected)


@pytest.mark.parametrize('source, expected', (
    # Minus
    (f'3{NBSP}-{NBSP}2', f'3{NBSP}{MINUS}{NBSP}2'),
    # This one clashes with range
    ('2-3', f'2{NDASH}3'),
    # This one clashes with mdash
    (f'x{NBSP}-{NBSP}3', f'x{NNBSP}{MDASH}{THNSP}3'),
    ('-3', f'{MINUS}3'),

    # Star
    ('3*2', f'3{TIMES}2'),
    ('*3', f'{TIMES}3'),
    (f'3{NBSP}*{NBSP}2', f'3{NBSP}{TIMES}{NBSP}2'),
    (f'x{NBSP}*{NBSP}2', f'x{NBSP}{TIMES}{NBSP}2'),

    # 'x'
    ('3x2', f'3{TIMES}2'),
    ('x3', f'{TIMES}3'),
    (f'3{NBSP}x{NBSP}2', f'3{NBSP}{TIMES}{NBSP}2'),
    (f'x{NBSP}x{NBSP}2', f'x{NBSP}{TIMES}{NBSP}2'),

    # and Russian "х"
    ('3х2', f'3{TIMES}2'),
    ('х3', f'{TIMES}3'),
    (f'3{NBSP}х{NBSP}2', f'3{NBSP}{TIMES}{NBSP}2'),
    (f'x{NBSP}х{NBSP}2', f'x{NBSP}{TIMES}{NBSP}2'),
))
def test_math(assert_typus, source, expected):
    assert_typus(source, expected)


@pytest.mark.parametrize('source, expected', (
    ('aaa 2a', f'aaa 2a'),  # doesnt clash with units
))
def test_pairs(assert_typus, source, expected):
    assert_typus(source, expected)


@pytest.mark.parametrize('source, expected', (
    ('4444444 fooo', '4444444 fooo'),
    ('444 foo', f'444{NBSP}foo'),
    ('444 +', f'444{NBSP}+'),
    ('444 4444 bucks', f'444{NBSP}4444 bucks'),
    ('4444444 foo', f'4444444 foo'),  # no untis clash
    ('444 -', f'444{NBSP}{MDASH}'),
))
def test_digit_spaces(assert_typus, source, expected):
    assert_typus(source, expected)


def test_example(assert_typus):
    source = (
        'Излучение, как следует из вышесказанного, концентрирует '
        'внутримолекулярный предмет - деятельности . "...ff \'Можно?\' '
        'предположить, что силовое - "поле "мент "d" ально" отклоняет" '
        'сенсибельный \'квазар !..\' cc", не учитывая мнения авторитетов. '
        'Искусство испускает данный электрон, учитывая опасность, '
        '<code> "d" test -- test(c)</code> которую    представляли '
        'собой писания Дюринга для не окрепшего еще немецкого рабочего '
        'движения. Смысл жизни -- амбивалентно (с) дискредитирует '
        'закон (r) исключённого(tm) третьего (тм)...      \n\n\n'
        '1500 мА*ч\n\n'
        '3-3=0\n'
        '- Химическое соединение (p) ненаблюдаемо контролирует экран-ый '
        'квазар (р). Идеи 3/4  гедонизма занимают b & b центральное место '
        'в утилитаризме(sm) "Милля и Бентама", однако <- гравитирующая -> '
        'сфера масштабирует фотон, +-2мм изменяя привычную == реальность. '
        'Силовое *3 поле -3 реально 3 * 2 /= 6   3x3 восстанавливает '
        'трансцендентальный 3" 2\' принцип 1000р. восприятия.'
        '"...\'test\'" (c) m&m\'s\n\n\n'
    )
    expected = (
        'Излучение, как следует из_вышесказанного, концентрирует '
        'внутримолекулярный предмет\u202f—\u2009деятельности. «…ff „Можно?“ '
        'предположить, что силовое\u202f—\u2009„поле «мент „d“ ально» '
        'отклоняет“ '
        'сенсибельный „квазар!..“ cc», не_учитывая мнения авторитетов. '
        'Искусство испускает данный электрон, учитывая опасность, '
        '<code> "d" test -- test(c)</code> которую представляли собой '
        'писания Дюринга для не_окрепшего еще немецкого рабочего '
        'движения. Смысл жизни\u202f—\u2009амбивалентно ©_дискредитирует '
        'закон® исключённого™ третьего™…\n\n'
        '1500_мА•ч\n\n'
        '3−3=0\n'
        '—_Химическое соединение℗ ненаблюдаемо контролирует экран-ый '
        'квазар℗. Идеи ¾_гедонизма занимают b_&_b_центральное место '
        'в_утилитаризме℠ «Милля и_Бентама», однако ←_гравитирующая_→ '
        'сфера масштабирует фотон, ±2_мм изменяя привычную_≡_реальность. '
        'Силовое ×3_поле −3_реально 3_×_2_≠_6 3×3 восстанавливает '
        'трансцендентальный 3″ 2′ принцип 1000_₽ восприятия.'
        '«…„test“» ©_m&m’s'
    ).replace('_', NBSP)
    assert_typus(source, expected)
