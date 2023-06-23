"""JSON Data structures"""

import typing


Array: typing.TypeAlias = list[typing.ForwardRef('Data')]
"""JSON Array"""

Object: typing.TypeAlias = dict[str, typing.ForwardRef('Data')]
"""JSON Object"""

Data: typing.TypeAlias = None | bool | int | float | str | Array | Object
"""JSON data type identifier."""


def equals(a: Data,
           b: Data
           ) -> bool:
    """Equality comparison of json serializable data.

    Tests for equality of data according to JSON format. Notably, ``bool``
    values are not considered equal to numeric values in any case. This is
    different from default equality comparison, which considers `False`
    equal to `0` and `0.0`; and `True` equal to `1` and `1.0`.

    Example::

        assert equals(0, 0.0) is True
        assert equals({'a': 1, 'b': 2}, {'b': 2, 'a': 1}) is True
        assert equals(1, True) is False

    """
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    if a != b:
        return False

    if isinstance(a, dict):
        return all(equals(a[key], b[key]) for key in a)
    elif isinstance(a, list):
        return all(equals(i, j) for i, j in zip(a, b))
    else:
        return True


def clone(data: Data) -> Data:
    """Deep clone data

    This function recursively creates new instances of array and object data
    based on input data. Resulting json data is equal to provided data.

    Example::

        x = {'a': [1, 2, 3]}
        y = clone(x)
        assert x is not y
        assert x['a'] is not y['a']
        assert equals(x, y)

    """
    if isinstance(data, list):
        return [clone(i) for i in data]

    if isinstance(data, dict):
        return {k: clone(v) for k, v in data.items()}

    return data


def flatten(data: Data
            ) -> typing.Iterable[Data]:
    """Flatten JSON data

    If `data` is array, this generator recursively yields result of `flatten`
    call with each element of input list. For other `Data` types, input data is
    yielded.

    Example::

        data = [1, [], [2], {'a': [3]}]
        result = [1, 2, {'a': [3]}]
        assert list(flatten(data)) == result

    """
    if isinstance(data, list):
        for i in data:
            yield from flatten(i)
    else:
        yield data
