# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import unittest
from builtins import *  # noqa

import mock
from typus import typus
from typus.base import TypusBase
from typus.decorators import escape_codeblocks


class EscapeCodeblocksOnlyTest(unittest.TestCase):
    @mock.patch.object(escape_codeblocks, '_restore_codeblocks',
                       return_value='test')
    def test_restore_codeblocks_call(self, mock_restore_codeblocks):
        test = escape_codeblocks(TypusBase())

        test('test')
        mock_restore_codeblocks.assert_not_called()

        test('<code>test</code>')
        mock_restore_codeblocks.assert_called_once()


class EscapeCodeblocksTypusTest(unittest.TestCase):
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

    def test_nested_codeblocks(self):
        # No nested codeblocks
        test = self.typus()
        with self.assertRaises(AssertionError):
            test('<code>dsfsdf <code>"test"</code> "sdfdf"</code>',
                 '<code>dsfsdf <code>"test"</code> "sdfdf"</code>')
