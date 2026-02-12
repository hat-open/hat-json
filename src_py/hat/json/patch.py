"""JSON Patch"""

import typing

import jsonpatch

from hat.json.data import Data, equals


_Pointer: typing.TypeAlias = list[str]


def diff(src: Data,
         dst: Data
         ) -> Data:
    """Generate JSON Patch diff.

    Example::

        src = [1, {'a': 2}, 3]
        dst = [1, {'a': 4}, 3]
        result = diff(src, dst)
        assert result == [{'op': 'replace', 'path': '/1/a', 'value': 4}]

    """
    return jsonpatch.JsonPatch.from_diff(src, dst).patch


def patch(data: Data,
          diff: Data
          ) -> Data:
    """Apply JSON Patch diff.

    Example::

        data = [1, {'a': 2}, 3]
        d = [{'op': 'replace', 'path': '/1/a', 'value': 4}]
        result = patch(data, d)
        assert result == [1, {'a': 4}, 3]

    """
    for op in diff:
        data = _apply_op(data, op)

    return data


def _apply_op(data: Data, op: Data) -> Data:

    if op['op'] == 'add':
        path = _parse_pointer(op['path'])
        return _add(data, path, op['value'])

    if op['op'] == 'remove':
        path = _parse_pointer(op['path'])
        return _remove(data, path)

    if op['op'] == 'replace':
        path = _parse_pointer(op['path'])
        return _replace(data, path, op['value'])

    if op['op'] == 'move':
        from_path = _parse_pointer(op['from'])
        to_path = _parse_pointer(op['path'])
        return _move(data, from_path, to_path)

    if op['op'] == 'copy':
        from_path = _parse_pointer(op['from'])
        to_path = _parse_pointer(op['path'])
        return _copy(data, from_path, to_path)

    if op['op'] == 'test':
        path = _parse_pointer(op['path'])
        return _test(data, path, op['value'])

    raise ValueError('unsupported operation')


def _add(data: Data, path: _Pointer, value: Data) -> Data:

    if not path:
        return value

    key, *rest = path

    if isinstance(data, list):
        if rest:
            idx = int(key)
            if not 0 <= idx < len(data):
                raise ValueError('invalid array index')

            return [*data[:idx], _add(data[idx], rest, value), *data[idx+1:]]

        else:
            if key == '-':
                return [*data, value]

            idx = int(key)
            if not 0 <= idx <= len(data):
                raise ValueError('invalid array index')

            return [*data[:idx], value, *data[idx:]]

    if isinstance(data, dict):
        if rest:
            if key not in data:
                raise ValueError('invalid object key')

            return {**data, key: _add(data[key], rest, value)}

        else:
            return {**data, key: value}

    raise ValueError('invalid data type')


def _remove(data: Data, path: _Pointer) -> Data:

    if not path:
        return None

    key, *rest = path

    if isinstance(data, list):
        idx = int(key)
        if not 0 <= idx < len(data):
            raise ValueError('invalid array index')

        if rest:
            return [*data[:idx], _remove(data[idx], rest), *data[idx+1:]]
        else:
            return [*data[:idx], *data[idx+1:]]

    if isinstance(data, dict):
        if key not in data:
            raise ValueError('invalid object key')

        if rest:
            return {**data, key: _remove(data[key], rest)}
        else:
            return {k: v for k, v in data.items() if k != key}


def _replace(data: Data, path: _Pointer, value: Data) -> Data:

    if not path:
        return value

    key, *rest = path

    if isinstance(data, list):
        idx = int(key)
        if not 0 <= idx < len(data):
            raise ValueError('invalid array index')

        if rest:
            return [*data[:idx], _replace(data[idx], rest, value),
                    *data[idx+1:]]
        else:
            return [*data[:idx], value, *data[idx+1:]]

    if isinstance(data, dict):
        if key not in data:
            raise ValueError('invalid object key')

        if rest:
            return {**data, key: _replace(data[key], rest, value)}
        else:
            return {**data, key: value}


def _move(data: Data, from_path: _Pointer, to_path: _Pointer) -> Data:
    if len(to_path) > len(from_path) and from_path == to_path[:len(from_path)]:
        raise ValueError("path can't be child of from")

    value = _get(data, from_path)
    return _add(_remove(data, from_path), to_path, value)


def _copy(data: Data, from_path: _Pointer, to_path: _Pointer) -> Data:
    value = _get(data, from_path)
    return _add(data, to_path, value)


def _test(data: Data, path: _Pointer, value: Data) -> Data:
    if not equals(value, _get(data, path)):
        raise ValueError('invalid value')


def _get(data: Data, path: _Pointer) -> Data:

    if not path:
        return data

    key, *rest = path

    if isinstance(data, list):
        idx = int(key)
        if not 0 <= idx < len(data):
            raise ValueError('invalid array index')

        return _get(data[idx], rest)

    if isinstance(data, dict):
        if key not in data:
            raise ValueError('invalid object key')

        return _get(data[key], rest)

    raise ValueError('invalid data type')


def _parse_pointer(pointer: str) -> _Pointer:
    if pointer == '':
        return []

    segments = pointer.split('/')
    if segments[0] != '':
        raise ValueError('invalid pointer')

    return [_unescape_pointer_segment(i) for i in segments[1:]]


def _unescape_pointer_segment(segment: str) -> str:
    return segment.replace('~1', '/').replace('~0', '~')


# check upstream changes in jsonpatch and validate performance impact

# def _monkeypatch_jsonpatch():
#     """Monkeypatch jsonpatch.

#     Patch incorrect value comparison between ``bool`` and numeric values when
#     diffing json serializable data.

#     Comparing `False` to `0` or `0.0`; and `True` to `1` or `1.0` incorrectly
#     results in no change.

#     """
#     def _compare_values(self, path, key, src, dst):

#         if isinstance(src, jsonpatch.MutableMapping) and \
#                 isinstance(dst, jsonpatch.MutableMapping):
#             self._compare_dicts(jsonpatch._path_join(path, key), src, dst)

#         elif isinstance(src, jsonpatch.MutableSequence) and \
#                 isinstance(dst, jsonpatch.MutableSequence):
#             self._compare_lists(jsonpatch._path_join(path, key), src, dst)

#         elif isinstance(src, bool) == isinstance(dst, bool) and src == dst:
#             pass

#         else:
#             self._item_replaced(path, key, dst)

#     jsonpatch.DiffBuilder._compare_values = _compare_values


# _monkeypatch_jsonpatch()
