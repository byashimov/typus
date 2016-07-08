from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
from builtins import *  # noqa
from functools import wraps

__all__ = ('re_compile', 'map_choices', 'idict', 'splinter')


def re_compile(pattern, flags=re.I | re.U | re.M | re.S):
    return re.compile(pattern, flags)


class idict(dict):
    """
    Case insensitive dict.
    WARNING: It provides Typus required features only.
    """

    def __init__(self, obj=None, **kwargs):
        obj = dict(obj, **kwargs) if obj else kwargs
        normalized = dict((key.lower(), value) for key, value in obj.items())
        super(idict, self).__init__(**normalized)

    def __getitem__(self, key):
        return super(idict, self).__getitem__(key.lower())


def map_choices(data, find=r'({0})', dict_class=idict):
    """
    For simple cases when you just need to map founds to those
    values in a dictionary.
    """
    options = dict_class(data)
    choices = '|'.join(re.escape(x) for x in options)
    pattern = find.format(choices)

    def replace(match):
        key = match.group(0)
        return options[key]
    return pattern, replace


def splinter(delimiter):
    """
    Almost like str.split() but can handle delimiter escaping.
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
