from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
from builtins import *  # noqa

__all__ = ('re_compile', 'map_choices')


def re_compile(pattern, flags=re.I | re.U | re.M | re.S):
    return re.compile(pattern, flags)


def map_choices(data, find=r'({0})'):
    """
    For simple cases when you just need to map founds to those
    values in a dictionary.
    """
    options = data.copy()
    choices = '|'.join(re.escape(x) for x in options)
    pattern = find.format(choices)
    return pattern, lambda match: options[match.groups()[0]]
