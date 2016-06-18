# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import unittest
import requests
from builtins import *  # noqa

import mock
from typus import typus
from typus.base import TypusBase
from typus.decorators import escape_html


class EscapeHtmlOnlyTest(unittest.TestCase):
    @mock.patch.object(escape_html, '_restore_html',
                       return_value='test')
    def test_restore_html_call(self, mock_restore_html):
        test = escape_html(TypusBase())

        test('test')
        mock_restore_html.assert_not_called()

        test('<code>test</code>')
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
