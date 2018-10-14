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

:py:class:`typus.core.TypusCore` runs :ref:`Processors` to do the job
which can be plugged in for desired configuration.
Here is a quick example:

.. testcode::

    from typus.core import TypusCore
    from typus.processors import EnQuotes

    class MyTypus(TypusCore):
        processors = (EnQuotes, )

    my_typus = MyTypus()
    assert my_typus('"quoted text"') == '“quoted text”'

:py:class:`typus.core.TypusCore` runs :py:class:`typus.processors.EnQuotes`
processor which improves *quotes* only.
