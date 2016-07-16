from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
from builtins import *  # noqa
from functools import wraps

__all__ = ('re_compile', 'idict', 'map_choices', 'splinter')


def re_compile(pattern, flags=re.I | re.U | re.M | re.S):
    """
    A shortcut to compile regex with predefined flags:
    :const:`re.I`, :const:`re.U`, :const:`re.M`, :const:`re.S`.

    :param str pattern: A string to compile pattern from.
    :param int flags: Python :mod:`re` module flags.

    >>> foo = re_compile('[a-z]')  # matches with 'test' and 'TEST'
    >>> bool(foo.match('TEST'))
    True
    >>> bar = re_compile('[a-z]', flags=0)  # doesn't match with 'TEST'
    >>> bool(bar.match('TEST'))
    False
    """

    return re.compile(pattern, flags)


class idict(dict):
    """
    Case-insensitive dictionary.

    :param mapping/iterable obj: An object to initialize new dictionary from
    :param `**kwargs`: ``key=value`` pairs to put in the new dictionary

    >>> foo = idict({'A': 0, 'b': 1}, bar=2)
    >>> foo['a'], foo['B'], foo['bAr']
    (0, 1, 2)

    .. caution::
        :class:`idict` is not a full-featured case-insensitive dictionary.
        As it's made for :func:`map_choices` it has limited functionality.
    """

    def __init__(self, obj=None, **kwargs):
        obj = dict(obj, **kwargs) if obj else kwargs
        normalized = dict((key.lower(), value) for key, value in obj.items())
        super(idict, self).__init__(**normalized)

    def __getitem__(self, key):
        return super(idict, self).__getitem__(key.lower())


def map_choices(data, group=r'({0})', dict_class=idict):
    """
    :class:`typus.processors.Expressions` helper.
    Builds regex pattern from the dictionary keys and maps them to values via
    replace function.

    :param mapping/iterable data: A pairs of (find, replace with) strings
    :param str group: A string to format in choices.
    :param class dict_class: A dictionary class to convert source data.
        By default :class:`idict` is used which is case-insensitive.
        In instance, to map  ``(c)`` and ``(C)`` to different values pass
        regular python :class:`dict`. Or if the order matters use
        :class:`collections.OrderedDict`

    :returns: A regex non-compiled pattern and replace function
    :rtype: tuple

    >>> import re
    >>> pattern, replace = map_choices({'a': 0, 'b': 1})
    >>> re.sub(pattern, replace, 'abc')
    '01c'
    """

    options = dict_class(data)
    choices = '|'.join(re.escape(x) for x in options)
    pattern = group.format(choices)

    def replace(match):
        key = match.group(0)
        return str(options[key])
    return pattern, replace


def splinter(delimiter):
    """
    :class:`typus.processors.EscapePhrases` helper.
    Almost like ``str.split()`` but handles delimiter escaping and strips
    spaces.

    :param str delimiter: String delimiter
    :raises ValueError: If delimiter is a slash or an empty space

    :returns: A list of stripped phrases splitted by the delimiter
    :rtype: list

    >>> split = splinter(',  ')  # strips this spaces
    >>> split('a, b,c ,  d\,e')  # and this ones too
    ['a', 'b', 'c', 'd,e']
    """

    delim = delimiter.strip(' \\')
    if not delim:
        raise ValueError('Delimiter can not be a slash or an empty space.')

    # Doesn't split escaped delimiters
    pattern = re.compile(r'(?<!\\){0}\s*'.format(re.escape(delim)))

    @wraps(splinter)
    def inner(phrases):
        # Deletes delimiter escaping and strips spaces
        return [x.replace('\\' + delim, delim).strip()
                for x in pattern.split(phrases)]
    return inner
