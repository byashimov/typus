import pytest

from typus import TypusCore, ru_typus


def test_empty_string(mocker):
    mocker.patch('typus.ru_typus.procs')
    assert ru_typus('') == ''
    ru_typus.procs.run.assert_not_called()


def test_debug_true():
    assert ru_typus('2mm', debug=True) == '2_mm'


def test_no_processors():
    class Testus(TypusCore):
        pass

    with pytest.raises(AssertionError):
        Testus()
