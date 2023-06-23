"""JSON Path"""

import collections
import itertools
import typing

from hat import util
from hat.json.data import Data, flatten


Path: typing.TypeAlias = int | str | list[typing.ForwardRef('Path')]
"""JSON Path"""


def get(data: Data,
        path: Path,
        default: Data | None = None
        ) -> Data:
    """Get data element referenced by path

    Example::

        data = {'a': [1, 2, [3, 4]]}
        path = ['a', 2, 0]
        assert get(data, path) == 3

        data = [1, 2, 3]
        assert get(data, 0) == 1
        assert get(data, 5) is None
        assert get(data, 5, default=123) == 123

    """
    for i in flatten(path):
        if isinstance(i, str):
            if not isinstance(data, dict) or i not in data:
                return default
            data = data[i]

        elif isinstance(i, int) and not isinstance(i, bool):
            if not isinstance(data, list):
                return default
            try:
                data = data[i]
            except IndexError:
                return default

        else:
            raise ValueError('invalid path')

    return data


def set_(data: Data,
         path: Path,
         value: Data
         ) -> Data:
    """Create new data by setting data path element value

    Example::

        data = [1, {'a': 2, 'b': 3}, 4]
        path = [1, 'b']
        result = set_(data, path, 5)
        assert result == [1, {'a': 2, 'b': 5}, 4]
        assert result is not data

        data = [1, 2, 3]
        result = set_(data, 4, 4)
        assert result == [1, 2, 3, None, 4]

    """
    parents = collections.deque()

    for i in flatten(path):
        parent = data

        if isinstance(i, str):
            data = data.get(i) if isinstance(data, dict) else None

        elif isinstance(i, int) and not isinstance(i, bool):
            try:
                data = data[i] if isinstance(data, list) else None
            except IndexError:
                data = None

        else:
            raise ValueError('invalid path')

        parents.append((parent, i))

    while parents:
        parent, i = parents.pop()

        if isinstance(i, str):
            parent = dict(parent) if isinstance(parent, dict) else {}
            parent[i] = value

        elif isinstance(i, int) and not isinstance(i, bool):
            if not isinstance(parent, list):
                parent = []

            if i >= len(parent):
                parent = [*parent,
                          *itertools.repeat(None, i - len(parent) + 1)]

            elif i < 0 and (-i) > len(parent):
                parent = [*itertools.repeat(None, (-i) - len(parent)),
                          *parent]

            else:
                parent = list(parent)

            parent[i] = value

        else:
            raise ValueError('invalid path')

        value = parent

    return value


def remove(data: Data,
           path: Path
           ) -> Data:
    """Create new data by removing part of data referenced by path

    Example::

        data = [1, {'a': 2, 'b': 3}, 4]
        path = [1, 'b']
        result = remove(data, path)
        assert result == [1, {'a': 2}, 4]
        assert result is not data

        data = [1, 2, 3]
        result = remove(data, 4)
        assert result == [1, 2, 3]

    """
    result = data
    parents = collections.deque()

    for i in flatten(path):
        parent = data

        if isinstance(i, str):
            if not isinstance(data, dict) or i not in data:
                return result
            data = data[i]

        elif isinstance(i, int) and not isinstance(i, bool):
            if not isinstance(data, list):
                return result
            try:
                data = data[i]
            except IndexError:
                return result

        else:
            raise ValueError('invalid path')

        parents.append((parent, i))

    result = None

    while parents:
        parent, i = parents.pop()

        if isinstance(i, str):
            parent = dict(parent)

        elif isinstance(i, int) and not isinstance(i, bool):
            parent = list(parent)

        else:
            raise ValueError('invalid path')

        if result is None:
            del parent[i]

        else:
            parent[i] = result

        result = parent

    return result


class Storage:
    """JSON data storage

    Helper class representing observable JSON data state manipulated with
    path based get/set/remove functions.

    """

    def __init__(self, data: Data = None):
        self._data = data
        self._change_cbs = util.CallbackRegistry()

    @property
    def data(self) -> Data:
        """Data"""
        return self._data

    def register_change_cb(self,
                           cb: typing.Callable[[Data], None]
                           ) -> util.RegisterCallbackHandle:
        """Register data change callback"""
        return self._change_cbs.register(cb)

    def get(self, path: Path, default: Data | None = None):
        """Get data"""
        return get(self._data, path, default)

    def set(self, path: Path, value: Data):
        """Set data"""
        self._data = set_(self._data, path, value)
        self._change_cbs.notify(self._data)

    def remove(self, path: Path):
        """Remove data"""
        self._data = remove(self._data, path)
        self._change_cbs.notify(self._data)
