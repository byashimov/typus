from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
from builtins import *  # noqa

__all__ = ('re_compile', 'map_choices')


def re_compile(pattern, flags=re.I | re.U | re.M | re.S):
    return re.compile(pattern, flags)


class idict(dict):
    """
    Case insensitive dict.
    WARNING: It provides Typus required features only.
    """

    def __init__(self, obj=None, **kwargs):
        obj = dict(obj, **kwargs) if obj else kwargs
        super(idict, self).__init__(**{key.lower(): value
                                       for key, value in obj.items()})

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
