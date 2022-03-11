import itertools

import pytest

from hat import json


@pytest.mark.parametrize("params, is_equal", [
    ((0, 0.0),
     True),

    ((0, 1E-9),
     False),

    ((-100, -100.0),
     True),

    ((True, True),
     True),

    (('a', 'a'),
     True),

    (({'a': 0, 'b': 1},
      {'b': 1, 'a': 0}),
     True),

    ((0, False, '', [], {}, None),
     False),

    (({'a': 0}, [0], 0),
     False),

    (([1, 2], [2, 1]),
     False),

    (([], [[]], [{}], [None], [0.0], [False], ['']),
     False),

    (({'a': None},
      {'a': []},
      {'a': {}},
      {'a': 0},
      {'a': False},
      {'a': ''}),
     False)
])
def test_equals(params, is_equal):
    for a, b in itertools.combinations(params, 2):
        assert json.equals(a, b) == is_equal


def test_equals_example():
    assert json.equals(0, 0.0) is True
    assert json.equals({'a': 1, 'b': 2}, {'b': 2, 'a': 1}) is True
    assert json.equals(1, True) is False


def test_clone_example():
    x = {'a': [1, 2, 3]}
    y = json.clone(x)
    assert x is not y
    assert x['a'] is not y['a']
    assert json.equals(x, y)


@pytest.mark.parametrize("data, result", [
    (None,
     [None]),

    (1,
     [1]),

    (True,
     [True]),

    ('xyz',
     ['xyz']),

    ({'a': [1, [2, 3]]},
     [{'a': [1, [2, 3]]}]),

    ([],
     []),

    ([1, 2, 3],
     [1, 2, 3]),

    ([[[]], []],
     []),

    ([1, [2, [], [[], 3]]],
     [1, 2, 3])
])
def test_flatten(data, result):
    x = list(json.flatten(data))
    assert json.equals(x, result)


def test_flatten_example():
    data = [1, [], [2], {'a': [3]}]
    result = [1, 2, {'a': [3]}]
    assert list(json.flatten(data)) == result
