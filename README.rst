Typus
=====

Typus is a typography tool. Try out the demo_.


Disclaimer
----------

This project is under development and not production ready *yet*.


Quickstart
----------

Install the package:

.. code-block:: console

    pip install -e git://github.com/byashimov/typus.git#egg=typus

Use it:

.. code-block:: python

    from typus import en_typus, ru_typus

    en_typus('"Beautiful is better than ugly." (c) Tim Peters.', debug=True)
    '“Beautiful is_better than ugly.” ©_Tim Peters.'  # _ for nbsp

    ru_typus('"Красивое лучше, чем уродливое." (с) Тим Петерс.')
    '«Красивое лучше, чем уродливое.» © Тим Петерс.'  # cyrillic 'с' in '(с)'


Documentation
-------------

Coming soon. If you speak Russian or know Google Translate, you may find `this article`_ quite helpful.


Compatibility
-------------

.. image:: https://travis-ci.org/byashimov/typus.svg?branch=develop
    :alt: Build Status
    :target: https://travis-ci.org/byashimov/typus

.. image:: https://codecov.io/gh/byashimov/typus/branch/develop/graph/badge.svg
    :alt: Codecov
    :target: https://codecov.io/gh/byashimov/typus

Tested on py 2.5, 2.6, 2.7, 3.3, 3.4, 3.5 and probably others, please run the tests if your version is not on list.

.. _demo: https://byashimov.com/typus/
.. _this article: https://habrahabr.ru/post/303608/
