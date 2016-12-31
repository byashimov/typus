Welcome to Typus
================

Typus is a typography tool. It means your can write text the way you use to
and let it handle all that formating headache:

::

    "I don't feel very much like Pooh today..." said Pooh.
    "There there," said Piglet. "I'll bring you tea and honey until you do."
    - A.A. Milne, Winnie-the-Pooh

    “I don’t feel very much like Pooh today…” said Pooh.
    “There there,” said Piglet. “I’ll bring you tea and honey until you do.”
    — A. A. Milne, Winnie-the-Pooh

Copy & paste this example to your rich text editor. Result may depend on
the font of your choice.
For instance, there is a tiny non-breakable space between ``A. A.`` you
can see with Helvetica:

.. image:: example.png


Installation
------------

.. code-block:: console

    pip install -e git://github.com/byashimov/typus.git#egg=typus


Usage
-----

Currently Typus supports English and Russian languages only.
Which doesn't mean it can't handle more. I'm quite sure it covers Serbian
and Turkmen.

In fact, Typus doesn't make difference between languages. It works with text.
If you use Cyrillic then only relative processors will affect that text.
In another words, give it a try if your language is not on the list

Here is a short example:

.. code-block:: python

    from typus import en_typus, ru_typus

    en_typus('"Beautiful is better than ugly." (c) Tim Peters.', debug=True)
    '“Beautiful is_better than ugly.” © Tim Peters.'  # nbsp after '©'

    ru_typus('"Красивое лучше, чем уродливое." (с) Тим Петерс.')
    '«Красивое лучше, чем уродливое.» © Тим Петерс.'  # cyrillic 'с' in '(с)'

The only difference between :func:`typus.en_typus` and :func:`typus.ru_typus`
are in quotes they set: ``“‘’”`` for English and ``«„“»`` for Russian. Both of
them handle mixed text and that is pretty awesome.

Typus is highly customizable. Not only quotes can be replaced but almost
everything. For instance, if you don't use html tags you can skip
:class:`typus.processors.EscapeHtml` processor which makes your Typus a little
faster.


What it does
------------

- Replaces regular quotes ``"foo 'bar' baz"`` with typographic pairs:
  ``“foo ‘bar’ baz”``. Quotes style depends on language and your Typus configuration.
- Replaces regular dash ``foo - bar`` with mdash or ndash or minus.
  Depends on case: plain text, digit rage, phone nubers, etc.
- Replaces complex symbols such as ``(c)`` with unicode characters: ``©``.
  Cyrillic analogs are supported too.
- Replaces vulgar fractions ``1/2`` with unicode characters: ``½``.
- Turns multiply symbol to a real one: ``3x3`` becomes ``3×3``.
- Replaces quotes with primes: ``2' 4"`` becomes ``2′ 4″``.
- Puts non-breakable spaces.
- Puts ruble symbol.
- Trims spaces at the end of lines.
- and much more.

Documentation
-------------

Docs are hosted on `readthedocs.org`_.

.. seealso::

    Oh, there is also an outdated Russian article I should not
    probably suggest, but since all docs are in English, this link_ might be
    quite helpful.


Compatibility
-------------

.. image:: https://travis-ci.org/byashimov/typus.svg?branch=develop
    :alt: Build Status
    :target: https://travis-ci.org/byashimov/typus

.. image:: https://codecov.io/gh/byashimov/typus/branch/develop/graph/badge.svg
    :alt: Codecov
    :target: https://codecov.io/gh/byashimov/typus

Tested on Python 2.5, 2.6, 2.7, 3.3, 3.4, 3.5, 3.6.


Todo
----

- Rewrite tests, they are ugly as hell.
- Add missing doctests.

.. _link: https://habrahabr.ru/post/303608/
.. _readthedocs.org: https://somewhere.com
.. _Mixins: https://somewhere.com