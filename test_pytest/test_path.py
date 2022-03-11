import collections

import pytest

from hat import json


@pytest.mark.parametrize("data, path, default, result", [
    (123,
     [],
     None,
     123),

    ('abc',
     [1, 'a', 2, 'b', 3],
     None,
     None),

    ({'a': [{'b': 1}, 2, 3]},
     ['a', 0, 'b'],
     None,
     1),

    ([1, 2, 3],
     0,
     None,
     1),

    ([1, 2, 3],
     -1,
     None,
     3),

    ([1, 2, 3],
     3,
     None,
     None),

    ([1, 2, 3],
     -4,
     None,
     None),

    ([1, 2, 3],
     -4,
     123,
     123),

    ([1, 2, 3],
     ['a'],
     'abc',
     'abc'),

    ({'a': 3},
     ['c'],
     456,
     456),

    ({'a': 3},
     [0],
     456,
     456),

    ({'a': [{'b': 1}, 2, 3]},
     ['a', 0, 'b', 0],
     [1, 2],
     [1, 2]),

    (None,
     ['a', 'b'],
     {'b': 123},
     {'b': 123})
])
def test_get(data, path, default, result):
    x = json.get(data, path, default)
    assert json.equals(x, result)


def test_get_example():
    data = {'a': [1, 2, [3, 4]]}
    path = ['a', 2, 0]
    assert json.get(data, path) == 3

    data = [1, 2, 3]
    assert json.get(data, 0) == 1
    assert json.get(data, 5) is None


def test_get_invalid_path():
    with pytest.raises(ValueError):
        json.get(None, True)


@pytest.mark.parametrize("data, path, value, result", [
    (123,
     [],
     'abc',
     'abc'),

    (None,
     ['a', 1],
     'x',
     {'a': [None, 'x']}),

    ({'a': [1, 2], 'b': 3},
     ['a', 1],
     4,
     {'a': [1, 4], 'b': 3}),

    ([1, 2, 3],
     4,
     'a',
     [1, 2, 3, None, 'a']),

    ([1, 2, 3],
     -5,
     'a',
     ['a', None, 1, 2, 3])
])
def test_set_(data, path, value, result):
    x = json.set_(data, path, value)
    assert json.equals(x, result)


def test_set_example():
    data = [1, {'a': 2, 'b': 3}, 4]
    path = [1, 'b']
    result = json.set_(data, path, 5)
    assert result == [1, {'a': 2, 'b': 5}, 4]
    assert result is not data

    data = [1, 2, 3]
    result = json.set_(data, 4, 4)
    assert result == [1, 2, 3, None, 4]


def test_set_invalid_path():
    with pytest.raises(ValueError):
        json.set_(None, True, 1)


@pytest.mark.parametrize("data, path, result", [
    (None,
     [],
     None),

    (123,
     [],
     None),

    ([1, {}, 'abc'],
     [],
     None),

    ([1, 2, 3],
     1,
     [1, 3]),

    ({'a': 1, 'b': 2},
     'a',
     {'b': 2}),

    ([1, {'a': [2, 3]}],
     [1, 'a', 0],
     [1, {'a': [3]}]),

    (123,
     123,
     123),

    ([1, 2, 3],
     5,
     [1, 2, 3]),

    ({'a': 123},
     'b',
     {'a': 123})
])
def test_remove(data, path, result):
    x = json.remove(data, path)
    assert json.equals(x, result)


def test_remove_example():
    data = [1, {'a': 2, 'b': 3}, 4]
    path = [1, 'b']
    result = json.remove(data, path)
    assert result == [1, {'a': 2}, 4]
    assert result is not data

    data = [1, 2, 3]
    result = json.remove(data, 4)
    assert result == [1, 2, 3]


def test_storage():
    data_queue = collections.deque()
    storage = json.Storage(123)
    storage.register_change_cb(data_queue.append)

    assert storage.data == 123
    assert storage.get([]) == 123

    storage.set(['a', 'b', 'c'], 123)
    assert storage.data == {'a': {'b': {'c': 123}}}
    assert storage.get(['a', 'b', 'c']) == 123
    assert data_queue.pop() == {'a': {'b': {'c': 123}}}

    storage.remove(['a', 'b', 'c'])
    assert storage.data == {'a': {'b': {}}}
    assert storage.get(['a', 'b', 'c']) is None
    assert data_queue.pop() == {'a': {'b': {}}}

    assert not data_queue
