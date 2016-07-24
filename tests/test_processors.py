# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
from builtins import *  # noqa

import mock
import requests
import unittest2
from typus import RuTypus, ru_typus
from typus.core import TypusCore
from typus.processors import BaseProcessor


class BaseProcessorTest(unittest2.TestCase):
    def test_base(self):
        class TestProcessor(BaseProcessor):
            "Empty processor with no __call__"

        class Testus(TypusCore):
            processors = (TestProcessor, )

        with self.assertRaises(NotImplementedError):
            Testus()


class EscapePhrasesTest(unittest2.TestCase):
    def typus(self):
        def inner(text, test, *args):
            self.assertEqual(ru_typus(text, escape_phrases=args), test)
        return inner

    def test_escaping(self):
        test = self.typus()
        test('"foo 2""', '«foo 2"»', '2"')
        test('"foo (c) (r) (tm)"', '«foo (c) (r) (tm)»', '(c)', '(r)', '(tm)')

        # Doesn't assert like the same one in EscapeHtmlTest
        test('<code>dsfsdf <code>"test"</code> "sdfdf"</code>',
             '<code>dsfsdf <code>"test"</code> "sdfdf"</code>',
             '<code>"test"</code>')

        # Empty string, nothing to escape
        test('"foo"', '«foo»', '')


class EscapeHtmlTest(unittest2.TestCase):
    def typus(self):
        return lambda text, test: self.assertEqual(ru_typus(text), test)

    @mock.patch('typus.processors.EscapeHtml.restore_values',
                return_value='test')
    def test_restore_html_call(self, mock_restore_values):
        ru_typus('test')
        mock_restore_values.assert_not_called()

        ru_typus('<code>test</code>')
        mock_restore_values.assert_called_once()

    def test_codeblocks(self):
        test = self.typus()
        test('<pre>"test"</pre>', '<pre>"test"</pre>')
        test('<code>"test"</code>', '<code>"test"</code>')

        # Nested code in pre
        test('<pre><code>"test"</code></pre>',
             '<pre><code>"test"</code></pre>')
        test('<pre><code><code>"test"</code></code></pre>',
             '<pre><code><code>"test"</code></code></pre>')

        # Script tag
        test('<script>"test"</script>', '<script>"test"</script>')
        test('<script type="text/javascript" src="/test/">"test"</script>',
             '<script type="text/javascript" src="/test/">"test"</script>')

    def test_nested_codeblocks(self):
        # No nested codeblocks
        test = self.typus()
        with self.assertRaises(AssertionError):
            test('<code>dsfsdf <code>"test"</code> "sdfdf"</code>',
                 '<code>dsfsdf <code>"test"</code> "sdfdf"</code>')

    def test_tags(self):
        test = self.typus()
        test('<b>"test"</b>', '<b>«test»</b>')
        test('<b id="test">"test"</b>', '<b id="test">«test»</b>')
        test('<b>"test"</b>', '<b>«test»</b>')

        # Image: html + xhtml
        test('<img>"test"', '<img>«test»')
        test('<img alt="test">"test"', '<img alt="test">«test»')
        test('<img alt="test"/>"test"', '<img alt="test"/>«test»')

    def test_comments(self):
        test = self.typus()
        test('<!-- "(c)" -->', '<!-- "(c)" -->')
        test('<!--"(c)"-->', '<!--"(c)"-->')
        test('<!---->', '<!---->')

    def test_doctype(self):
        test = self.typus()
        test('<!DOCTYPE html>', '<!DOCTYPE html>')
        test('<?xml version="1.0" encoding="UTF-8"?>',
             '<?xml version="1.0" encoding="UTF-8"?>')

    def test_head(self):
        test = self.typus()
        test('<head><title>(c)</title></head>',
             '<head><title>(c)</title></head>')

    def test_iframe(self):
        test = self.typus()
        test('<iframe height="500" width="500">(c)</iframe>',
             '<iframe height="500" width="500">(c)</iframe>')

    @unittest2.skipIf(os.getenv('TYPUS_SKIP_W3_TEST'), 'Leave for CI')
    def test_html_page(self):
        # It's almost blind test
        url = 'https://validator.w3.org/nu/'
        html_page = requests.get(url)
        processed = ru_typus(html_page.text)
        validator = requests.post(url + '?out=json',
                                  processed.encode('utf8'),
                                  headers={'content-type': 'text/html; '
                                                           'charset=utf-8'})
        self.assertEqual(validator.json(), {'messages': []})


class TypoQuotes(unittest2.TestCase):
    class Testus(RuTypus):
        expressions = ''

    def typus(self):
        testus = self.Testus()
        return lambda text, test: self.assertEqual(testus(text), test)

    @mock.patch('typus.processors.TypoQuotes.switch_nested',
                return_value='test')
    def test_switch_nested_call(self, mock_switch_nested):
        test = self.Testus()

        # No quotes
        test('00 11 00')
        mock_switch_nested.assert_not_called()

        # Odd only
        test('00 "11" 00')
        mock_switch_nested.assert_not_called()

        # Both
        test('"00 "11" 00"')
        mock_switch_nested.assert_called_once()

    def test_quotes(self):
        test = self.typus()

        # Levels
        test('00 "11" 00', '00 «11» 00')  # One
        test('"00 "11" 00"', '«00 „11“ 00»')  # Two
        test('00" "11 "22" 11"', '00" «11 „22“ 11»')  # Tree

        # Hardcore
        test('00 ""22"" 00', '00 «„22“» 00')
        test('00 ""22..."" 00', '00 «„22...“» 00')
        test('00 ""22"..." 00', '00 «„22“...» 00')
        test('"© test"', '«© test»')
        test('("test")', '(«test»)')
        test('"test"*', '«test»*')
        test('"test"®', '«test»®')
        test('"""test"""', '«„«test»“»')
        test('""""test""""', '«„«„test“»“»')
        test('"""""""test"""""""', '«„«„«„«test»“»“»“»')
        test('" test"', '" test"')
        test('" "test""', '" «test»"')
        test('"foo 2\'"', '«foo 2\'»')

        # False positive
        test('"foo 2""', '«foo 2»"')

        # Weired cases
        test('00 "... "22"" 00', '00 «... „22“» 00')
        test('00 "..."22"" 00', '00 «...„22“» 00')

        # Punctuation
        test('00 "...11 "22!"" 00', '00 «...11 „22!“» 00')
        test('00 "11 "22!"..." 00', '00 «11 „22!“...» 00')
        test('00 "11 "22!"?!." 00', '00 «11 „22!“?!.» 00')
        test('00 "11 "22!"?!."? 00', '00 «11 „22!“?!.»? 00')

        # Nested on side
        test('00 ""22!" 11" 00', '00 «„22!“ 11» 00')
        test('00 "11 "22?"" 00', '00 «11 „22?“» 00')

        # Different quotes
        test('00 "“22”" 00', '00 «„22“» 00')
        test('00 "‘22’" 00', '00 «„22“» 00')

        # Inches, minutes within quotes
        test('00 "11\'" 00 "11"', '00 «11\'» 00 «11»')
        test('00" "11" 00 "11"', '00" «11» 00 «11»')

        # Fire them all!
        test('''00" "11 '22' 11"? "11 '22 "33 33"' 11" 00' "11 '22' 11" 00"''',
             '00" «11 „22“ 11»? «11 „22 «33 33»“ 11» 00\' «11 „22“ 11» 00"')

    def test_me(self):
        test = self.typus()
        # Html test
        test('<span>"11"</span>', '<span>«11»</span>')
        test('"<span>11</span>"', '«<span>11</span>»')
