What it's for?
==============

Well, when you write text you make sure it's grammatically correct.
Typography is *an aesthetic* grammar. Everything you type should be typographied
in order to respect the reader. For instance, when you write *“you’re”* you
put *apostrophe* instead of *single quote*, because of the same reason you
place dot at the end of sentence instead of comma, even though they look
similar.

Unfortunately all typographic characters are well hidden in your keyboard
layout which makes them almost impossible to use. Fortunately Typus can do
that for you.


The anatomy
-----------

Typus uses :ref:`Processors` to do the job and :ref:`Mixins` as
those settings. And there is a :py:class:`typus.core.TypusCore`
class which makes all of them work together. Here is a quick example:

.. testcode::

    from typus.core import TypusCore
    from typus.mixins import EnQuotes
    from typus.processors import Quotes

    class MyTypus(EnQuotes, TypusCore):
        processors = (Quotes, )

    my_typus = MyTypus()
    assert my_typus('"quoted text"') == '“quoted text”'

:py:class:`typus.core.TypusCore` runs :py:class:`typus.processors.Quotes`
processor which uses *quotes* configuration from
:py:class:`typus.mixins.EnQuotes`.
