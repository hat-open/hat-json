"""JSON Patch"""

import typing

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
    return list(_diff(src, dst))


def _diff(src: Data,
          dst: Data,
          pointer: _Pointer = []) -> typing.Iterable[Data]:

    if _shallow_equals(src, dst):
        return

    if isinstance(src, list) and isinstance(dst, list):

        if not src and not dst:
            return

        if not src or not dst:
            yield {'op': 'replace',
                   'path': _format_pointer(pointer),
                   'value': dst}
            return

        if len(src) == len(dst):
            for i in range(len(src)):
                yield from _diff(src[i], dst[i], [*pointer, str(i)])

        elif len(src) > len(dst):
            dst_i = 0
            to_remove = len(src) - len(dst)

            for src_i in range(len(src)):

                if dst_i < len(dst) and _shallow_equals(src[src_i],
                                                        dst[dst_i]):
                    dst_i += 1

                elif to_remove > 0:
                    yield {'op': 'remove',
                           'path': _format_pointer([*pointer, str(dst_i)])}
                    to_remove -= 1

                else:
                    yield from _diff(src[src_i], dst[dst_i],
                                     [*pointer, str(dst_i)])
                    dst_i += 1

        else:
            src_i = 0
            to_add = len(dst) - len(src)

            for dst_i in range(len(dst)):

                if src_i < len(src) and _shallow_equals(src[src_i],
                                                        dst[dst_i]):
                    src_i += 1

                elif to_add > 0:
                    yield {'op': 'add',
                           'path': _format_pointer([*pointer, str(dst_i)]),
                           'value': dst[dst_i]}
                    to_add -= 1

                else:
                    yield from _diff(src[src_i], dst[dst_i],
                                     [*pointer, str(dst_i)])
                    src_i += 1

    elif isinstance(src, dict) and isinstance(dst, dict):

        if not src and not dst:
            return

        if not src or not dst:
            yield {'op': 'replace',
                   'path': _format_pointer(pointer),
                   'value': dst}
            return

        for k in src:

            if k not in dst:
                yield {'op': 'remove', 'path': _format_pointer([*pointer, k])}

        for k in dst:

            if k not in src:
                yield {'op': 'add',
                       'path': _format_pointer([*pointer, k]),
                       'value': dst[k]}

            else:
                yield from _diff(src[k], dst[k], [*pointer, k])

    else:
        yield {'op': 'replace',
               'path': _format_pointer(pointer),
               'value': dst}


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


def _format_pointer(pointer: _Pointer) -> str:
    if not pointer:
        return ''

    return '/' + '/'.join(_escape_pointer_segment(i) for i in pointer)


def _parse_pointer(pointer: str) -> _Pointer:
    if pointer == '':
        return []

    segments = pointer.split('/')
    if segments[0] != '':
        raise ValueError('invalid pointer')

    return [_unescape_pointer_segment(i) for i in segments[1:]]


def _escape_pointer_segment(segment: str) -> str:
    return segment.replace('~', '~0').replace('/', '~1')


def _unescape_pointer_segment(segment: str) -> str:
    return segment.replace('~1', '/').replace('~0', '~')


def _shallow_equals(a: Data, b: Data):
    if isinstance(a, (list, dict)) or isinstance(b, (list, dict)):
        return a is b

    return equals(a, b)
