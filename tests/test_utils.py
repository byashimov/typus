# pylint: disable=anomalous-backslash-in-string

import pytest

from typus.utils import idict, splinter


@pytest.mark.parametrize('source, expected', (
    ({'A': 0, 'b': 1, 'BAr': 2}, {'a': 0, 'b': 1, 'bar': 2}),
))
def test_idict(source, expected):
    result = idict(source)
    assert result == expected
    assert source != result


@pytest.mark.parametrize('source, expected', (
    ('a, b,c', ['a', 'b', 'c']),
    ('a, b\,c', ['a', 'b,c']),
))
def test_splinter_basic(source, expected):
    split = splinter(',')
    assert split(source) == expected


@pytest.mark.parametrize('source', (
    '\\', '\\  ', '  ',
))
def test_splinter_junk_delimiter(source):
    with pytest.raises(ValueError):
        splinter(source)


@pytest.mark.parametrize('source, expected', (
    (' a; b;c', ['a', 'b', 'c']),
    (' a; b ;c', ['a', 'b', 'c']),
    (' a; b ;c ', ['a', 'b', 'c']),
))
def test_splinter_positional_spaces(source, expected):
    split = splinter(';')
    assert split(source) == expected


def test_splinter_delimiter_with_spaces():
    split = splinter(' @  ')
    assert split('a@ b@ c ') == ['a', 'b', 'c']


def test_splinter_regex_delimiter():
    split = splinter('$')
    assert split('a$b$c') == ['a', 'b', 'c']


def test_splinter_doesnt_remove_other_slashes():
    split = splinter('*')
    assert split('a * b * c\*c \\b') == ['a', 'b', 'c*c \\b']
