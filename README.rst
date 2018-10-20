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
For instance, there is a tiny non-breaking space between ``A. A.`` you
can see with Helvetica:

.. image:: https://raw.githubusercontent.com/byashimov/typus/develop/docs/example.png

Try out the demo_.


Web API
-------

A tiny `web-service`_ for whatever legal purpose it may serve.


Installation
------------

.. code-block:: console

    $ pip install git+git://github.com/byashimov/typus.git#egg=typus


Usage
-----

Currently Typus supports English and Russian languages only.
But it doesn't mean it can't handle more. I'm quite sure it covers Serbian
and Turkmen.

In fact, Typus doesn't make difference between languages. It works with text.
If you use Cyrillic then only relative processors will affect that text.
In another words, give it a try if your language is not on the list

Here is a short example:

.. code-block:: python

    >>> from typus import en_typus, ru_typus
    ...
    >>> # Underscore is for nbsp in debug mode
    >>> en_typus('"Beautiful is better than ugly." (c) Tim Peters.', debug=True)
    '“Beautiful is_better than ugly.” ©_Tim Peters.'
    >>> # Cyrillic 'с' in '(с)'
    >>> ru_typus('"Красивое лучше, чем уродливое." (с) Тим Петерс.', debug=True)
    '«Красивое лучше, чем уродливое.» ©_Тим Петерс.'


The only difference between ``en_typus`` and ``ru_typus``
are in quotes they set: ``“‘’”`` for English and ``«„“»`` for Russian. Both of
them handle mixed text and that is pretty awesome.

Typus is highly customizable. Not only quotes can be replaced but almost
everything. For instance, if you don't use html tags you can skip
``EscapeHtml`` processor which makes your Typus a little
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
- Puts non-breaking spaces.
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

Tested on Python 3.6 but should work on any 3.x version.

.. _demo: https://byashimov.com/typus/
.. _web-service: https://byashimov.com/typus/api/
.. _readthedocs.org: http://py-typus.readthedocs.io/en/latest/
.. _link: https://habrahabr.ru/post/303608/
