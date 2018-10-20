# pylint: disable=anomalous-backslash-in-string

import re
from functools import wraps
from typing import Callable, Iterable, List

__all__ = (
    'RE_SCASE',
    'RE_ICASE',
    'doc_map',
    'idict',
    'map_choices',
    're_choices',
    're_compile',
    'splinter',
)


RE_SCASE = re.U | re.M | re.S  # sensitive case
RE_ICASE = re.I | RE_SCASE  # insensitive case


def re_compile(pattern: str, flags: int = RE_ICASE):
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


def re_choices(choices: Iterable[str], group: str = r'({})') -> str:
    """
    Returns regex group of escaped choices.

    :param choices: Iterable of strings.
    :param group: A string to format the group with.

    >>> re_choices(('foo', 'bar'))
    '(foo|bar)'
    """
    return group.format('|'.join(map(re.escape, choices)))


class idict(dict):
    """
    Case-insensitive dictionary.

    :param mapping/iterable obj: An object to initialize new dictionary from
    :param `**kwargs`: ``key=value`` pairs to put in the new dictionary
    :returns: A regex non-compiled pattern
    :rtype: str

    >>> foo = idict({'A': 0, 'b': 1, 'bar': 2})
    >>> foo['a'], foo['B'], foo['bAr']
    (0, 1, 2)

    .. caution::
        :class:`idict` is not a full-featured case-insensitive dictionary.
        As it's made for :func:`map_choices` and has limited functionality.
    """

    def __init__(self, obj: dict):
        lowered = ((key.lower(), value) for key, value in obj.items())
        super().__init__(lowered)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())


def map_choices(data: dict, group: str = r'({})', dict_class=idict) -> tuple:
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
    pattern = re_choices(options, group=group)

    def replace(match):
        return str(options[match.group()])
    return pattern, replace


def doc_map(data: dict, keys='Before', values='After', delim='|'):
    rows = '\n'.join(f'\t``{k}`` {delim} ``{v}``' for k, v in data.items())
    table = (
        f'\n.. csv-table::'
        f'\n\t:delim: {delim}'
        f'\n\t:header: "{keys}", "{values}"\n'
        f'\n{rows}'
    )

    def updater(func):
        func.__doc__ += table
        return func
    return updater


def splinter(delimiter: str) -> Callable[[str], List[str]]:
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
    replace = '\\' + delim

    @wraps(splinter)
    def inner(phrases: str):
        # Deletes delimiter escaping and strips spaces
        return [
            x.replace(replace, delim).strip()
            for x in pattern.split(phrases)
        ]
    return inner
