# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import mock
import unittest
import requests
from builtins import *  # noqa

from typus import typus, Typus


class EscapeHtmlOnlyTest(unittest.TestCase):
    @mock.patch('typus.processors.EscapeHtml._restore_html',
                return_value='test')
    def test_restore_html_call(self, mock_restore_html):
        typus('test')
        mock_restore_html.assert_not_called()

        typus('<code>test</code>')
        mock_restore_html.assert_called_once()


class EscapeHtmlTypusTest(unittest.TestCase):
    def typus(self):
        return lambda text, test: self.assertEqual(typus(text), test)

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

    def test_html_page(self):
        # It's almost blind test
        url = 'https://validator.w3.org/nu/'
        html_page = requests.get(url)
        processed = typus(html_page.text)
        validator = requests.post(url + '?out=json',
                                  processed.encode('utf8'),
                                  headers={'content-type': 'text/html; '
                                                           'charset=utf-8'})
        self.assertEqual(validator.json(), {'messages': []})


class QuotesProcessorTest(unittest.TestCase):
    class Testus(Typus):
        expressions = ''

    def typus(self):
        testus = self.Testus()
        return lambda text, test: self.assertEqual(testus(text), test)

    @mock.patch('typus.processors.TypoQuotes._fix_nesting',
                return_value='test')
    def test_fix_nesting_call(self, mock_fix_nesting):
        test = self.Testus()
        test('00 "11" 00')
        mock_fix_nesting.assert_not_called()

        test('"00 "11" 00"')
        mock_fix_nesting.assert_called_once()

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
        test('" test"', '" test"')
        test('" "test""', '" «test»"')

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
