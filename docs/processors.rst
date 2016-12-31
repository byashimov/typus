.. _Processors:

Processors
==========

Processors are the core of Typus. Multiple processors are nested and chained
in one single function to do things which may depend on the result returned by
inner processors. Say, we set ``EscapeHtml`` and ``MyTrimProcessor``,
this is how it works:

::

    extract html tags
        pass text further if condition is true
            do something and return
        return the text
    put tags back and return

In python:

.. testcode::

    from typus.core import TypusCore
    from typus.processors import BaseProcessor, EscapeHtml

    class MyTrimProcessor(BaseProcessor):
        def __call__(self, func):
            def inner(text, *args, **kwargs):
                # When processor is initiated it gets typus instance
                # as the first argument so you can access to it's configuration
                # any time
                if self.typus.trim:
                    trimmed = text.strip()
                else:
                    trimmed = text
                return func(trimmed, *args, **kwargs)
            return inner

    class MyTypus(TypusCore):
        # This becomes a single function. EscapeHtml goes first
        processors = (EscapeHtml, MyTrimProcessor)

        # Set it `False` to disable trimming
        trim = True

    my_typus = MyTypus()
    assert my_typus('    test    ') == 'test'


Processors can be configured with :ref:`Mixins`.


Built-in processors
-------------------

.. automodule:: typus.processors
    :members: