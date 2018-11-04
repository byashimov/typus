from unittest import mock

import pytest

from typus import EscapeHtml, EscapePhrases, RuQuotes, TypusCore, ru_typus


@pytest.mark.parametrize('source, expected, escape_phrases', (
    ('"foo 2""', '«foo 2"»', ['2"']),
    ('"foo (c) (r) (tm)"', '«foo (c) (r) (tm)»', ['(c)', '(r)', '(tm)']),

    # Doesn't assert like the same one in EscapeHtmlTest
    (
        '<code>dsfsdf <code>"test"</code> "sdfdf"</code>',
        '<code>dsfsdf <code>"test"</code> "sdfdf"</code>',
        ['<code>"test"</code>'],
    ),

    # Empty string, nothing to escape
    ('"foo"', '«foo»', ['']),
))
def test_escape_phrases(source, expected, escape_phrases):
    assert ru_typus(source, escape_phrases=escape_phrases) == expected


@mock.patch('typus.processors.EscapeHtml._restore_values', return_value='test')
def test_restore_html_call(mock_restore_values):
    ru_typus('test')
    mock_restore_values.assert_not_called()

    ru_typus('<code>test</code>')
    mock_restore_values.assert_called_once()


@pytest.mark.parametrize('source', (
    '<pre>"test"</pre>',
    '<code>"test"</code>',

    # Nested code in pre
    '<pre><code>"test"</code></pre>',
    '<pre><code><code>"test"</code></code></pre>',

    # Script tag
    '<script>"test"</script>',
    '<script type="text/javascript" src="/test/">"test"</script>',
))
def test_codeblocks(source):
    assert ru_typus(source) == source


@pytest.mark.parametrize('source, expected', (
    (
        '<code>dsfsdf <code>"test"</code> "sdfdf"</code>',
        '<code>dsfsdf <code>"test"</code> «sdfdf»</code>',
    ),
))
def test_nested_codeblocks(typus, source, expected):
    # No nested codeblocks
    assert typus(source) == expected


@pytest.mark.parametrize('source, expected', (
    ('<b>"test"</b>', '<b>«test»</b>'),
    ('<b id="test">"test"</b>', '<b id="test">«test»</b>'),
    ('<b>"test"</b>', '<b>«test»</b>'),

    # Image: html + xhtml
    ('<img>"test"', '<img>«test»'),
    ('<img alt="test">"test"', '<img alt="test">«test»'),
    ('<img alt="test"/>"test"', '<img alt="test"/>«test»'),
))
def test_tags(source, expected):
    assert ru_typus(source) == expected


@pytest.mark.parametrize('source', (
    '<!-- "(c)" -->',
    '<!--"(c)"-->',
    '<!---->',
))
def test_comments(source):
    assert ru_typus(source) == source


@pytest.mark.parametrize('source', (
    '<!DOCTYPE html>',
    '<?xml version="1.0" encoding="UTF-8"?>',
))
def test_doctype(source):
    assert ru_typus(source) == source


@pytest.mark.parametrize('source', (
    '<head><title>(c)</title></head>',
))
def test_head(source):
    assert ru_typus(source) == source


@pytest.mark.parametrize('source', (
    '<iframe height="500" width="500">(c)</iframe>',
))
def test_iframe(source):
    assert ru_typus(source) == source


@pytest.fixture(name='typus')
def get_typus():
    class Typus(TypusCore):
        processors = (
            EscapePhrases,
            EscapeHtml,
            RuQuotes,
        )

    return Typus()


@mock.patch('typus.processors.BaseQuotes._switch_nested', return_value='test')
def test_switch_nested_call(mock_switch_nested, typus):
    # No quotes
    typus('00 11 00')
    mock_switch_nested.assert_not_called()

    # Odd only
    typus('00 "11" 00')
    mock_switch_nested.assert_not_called()

    # Both
    typus('"00 "11" 00"')
    mock_switch_nested.assert_called_once()


@pytest.mark.parametrize('source, expected', (
    # Levels
    ('00 "11" 00', '00 «11» 00'),  # One
    ('"00 "11" 00"', '«00 „11“ 00»'),  # Two
    ('00" "11 "22" 11"', '00" «11 „22“ 11»'),  # Tree

    # Hardcore
    ('00 ""22"" 00', '00 «„22“» 00'),
    ('00 ""22..."" 00', '00 «„22...“» 00'),
    ('00 ""22"..." 00', '00 «„22“...» 00'),
    ('"© test"', '«© test»'),
    ('("test")', '(«test»)'),
    ('"test"*', '«test»*'),
    ('"test"®', '«test»®'),
    ('"""test"""', '«„«test»“»'),
    ('""""test""""', '«„«„test“»“»'),
    ('"""""""test"""""""', '«„«„«„«test»“»“»“»'),
    ('" test"', '" test"'),
    ('" "test""', '" «test»"'),
    ('"foo 2\'"', '«foo 2\'»'),

    # False positive
    ('"foo 2""', '«foo 2»"'),

    # Weired cases
    ('00 "... "22"" 00', '00 «... „22“» 00'),
    ('00 "..."22"" 00', '00 «...„22“» 00'),

    # Punctuation
    ('00 "...11 "22!"" 00', '00 «...11 „22!“» 00'),
    ('00 "11 "22!"..." 00', '00 «11 „22!“...» 00'),
    ('00 "11 "22!"?!." 00', '00 «11 „22!“?!.» 00'),
    ('00 "11 "22!"?!."? 00', '00 «11 „22!“?!.»? 00'),

    # Nested on side
    ('00 ""22!" 11" 00', '00 «„22!“ 11» 00'),
    ('00 "11 "22?"" 00', '00 «11 „22?“» 00'),

    # Different quotes
    ('00 "“22”" 00', '00 «„22“» 00'),
    ('00 "‘22’" 00', '00 «„22“» 00'),

    # Inches, minutes within quotes
    ('00 "11\'" 00 "11"', '00 «11\'» 00 «11»'),
    ('00" "11" 00 "11"', '00" «11» 00 «11»'),

    # Fire them all!
    (
        '''00" "11 '22' 11"? "11 '22 "33 33"' 11" 00' "11 '22' 11" 00"''',
        '00" «11 „22“ 11»? «11 „22 «33 33»“ 11» 00\' «11 „22“ 11» 00"',
    ),
))
def test_quotes(typus, source, expected):
    assert typus(source) == expected


@pytest.mark.parametrize('source, expected', (
    # Html test
    ('<span>"11"</span>', '<span>«11»</span>'),
    ('"<span>11</span>"', '«<span>11</span>»'),
))
def test_me(typus, source, expected):
    assert typus(source) == expected
