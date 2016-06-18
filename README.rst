Typus
=====

Russian language typographer.


Disclamer
---------

This project is under development and not production ready *yet*.


Quickstart
----------

Install the package:

.. code-block:: console

    pip install -e git://github.com/byashimov/typus.git#egg=typus

Use it:

.. code-block:: python

    from typus import typus

    typus('"Красивое лучше, чем уродливое." (с) Тим Петерс.')
    '«Красивое лучше, чем уродливое.» ©_Тим Петерс.'  # _ is nbsp


Documentation
-------------

Coming soon.


Compatability
-------------

.. image:: https://travis-ci.org/byashimov/typus.svg?branch=develop
    :alt: Build Status
    :target: https://travis-ci.org/byashimov/typus

.. image:: https://codecov.io/gh/byashimov/typus/branch/develop/graph/badge.svg
    :alt: Codecov
    :target: https://codecov.io/gh/byashimov/typus

Tested on py 2.5, 2.6, 2.7, 3.3, 3.4, 3.5 and probably others, please run the tests if your version is not on list.