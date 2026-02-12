import pytest

from hat import json


data = {'a': [1, 2, [[], 123], {'b': 'abc'}],
        'c': True}


@pytest.mark.parametrize("x, y, diff", [
    ({'a': 0},
     {'a': False},
     [{'op': 'replace', 'path': '/a', 'value': False}]),

    ({'a': ""},
     {'a': False},
     [{'op': 'replace', 'path': '/a', 'value': False}]),

    ({'a': False},
     {'a': False},
     []),

    ({'a': []},
     {'a': {}},
     [{'op': 'replace', 'path': '/a', 'value': {}}]),

    ({'a': False},
     {'a': None},
     [{'op': 'replace', 'path': '/a', 'value': None}]),

    # TODO should we consider 1 and 1.0 to be equal
    ({'a': 1.0},
     {'a': 1},
     [{'op': 'replace', 'path': '/a', 'value': 1.0}]),

    ({'a': ""},
     {'a': []},
     [{'op': 'replace', 'path': '/a', 'value': []}]),

    ({'a': {}},
     {'a': {}},
     []),

    ({'a': ""},
     {'a': ""},
     []),

    ({'a': []},
     {'a': []},
     [])
])
def test_diff(x, y, diff):
    result = json.diff(x, y)
    assert json.equals(result, diff)


@pytest.mark.parametrize("x", [[], {}, 1, False, 'a', None])
def test_patch_empty(x):
    result = json.patch(x, [])
    assert json.equals(result, x)


@pytest.mark.parametrize("x, diff, y", [
    (data,
     [{'op': 'add', 'path': '', 'value': 42}],
     42),

    (data,
     [{'op': 'add', 'path': '/a/3/b', 'value': 'cba'}],
     json.set_(data, ['a', 3, 'b'], 'cba')),

    (data,
     [{'op': 'add', 'path': '/a/2/0/-', 'value': 42}],
     json.set_(data, ['a', 2, 0, 0], 42)),

    (data,
     [{'op': 'add', 'path': '/a/2/0/0', 'value': 42}],
     json.set_(data, ['a', 2, 0, 0], 42)),

    (data,
     [{'op': 'add', 'path': '/a/2/0', 'value': 321}],
     json.set_(data, ['a', 2], [321, [], 123]))
])
def test_patch_add(x, diff, y):
    result = json.patch(x, diff)
    assert json.equals(result, y)


@pytest.mark.parametrize("x, diff, y", [
    (data,
     [{'op': 'remove', 'path': ''}],
     None),

    (data,
     [{'op': 'remove', 'path': '/a/3/b'}],
     json.remove(data, ['a', 3, 'b'])),

    (data,
     [{'op': 'remove', 'path': '/a/2/0'}],
     json.remove(data, ['a', 2, 0]))
])
def test_patch_remove(x, diff, y):
    result = json.patch(x, diff)
    assert json.equals(result, y)


@pytest.mark.parametrize("x, diff, y", [
    (data,
     [{'op': 'replace', 'path': '', 'value': 42}],
     42),

    (data,
     [{'op': 'replace', 'path': '/a/3/b', 'value': 'cba'}],
     json.set_(data, ['a', 3, 'b'], 'cba')),

    (data,
     [{'op': 'replace', 'path': '/a/2/0', 'value': 321}],
     json.set_(data, ['a', 2, 0], 321))
])
def test_patch_replace(x, diff, y):
    result = json.patch(x, diff)
    assert json.equals(result, y)


@pytest.mark.parametrize("x, diff, y", [
    (data,
     [{'op': 'move', 'from': '', 'path': ''}],
     data),

    (data,
     [{'op': 'move', 'from': '/c', 'path': '/a'}],
     {'a': True})
])
def test_patch_move(x, diff, y):
    result = json.patch(x, diff)
    assert json.equals(result, y)


@pytest.mark.parametrize("x, diff, y", [
    (data,
     [{'op': 'copy', 'from': '', 'path': ''}],
     data),

    (data,
     [{'op': 'copy', 'from': '/c', 'path': '/a'}],
     {'a': True, 'c': True})
])
def test_patch_copy(x, diff, y):
    result = json.patch(x, diff)
    assert json.equals(result, y)


@pytest.mark.parametrize("x, diff, success", [
    (data,
     [{'op': 'test', 'path': '', 'value': data}],
     True),

    (data,
     [{'op': 'test', 'path': '/a/3', 'value': {'b': 'abc'}}],
     True),

    (data,
     [{'op': 'test', 'path': '/a/3', 'value': {'b': 'def'}}],
     False),

    (1,
     [{'op': 'test', 'path': '', 'value': True}],
     False)
])
def test_patch_test(x, diff, success):
    if success:
        json.patch(x, diff)
    else:
        with pytest.raises(ValueError):
            json.patch(x, diff)


def test_diff_example():
    src = [1, {'a': 2}, 3]
    dst = [1, {'a': 4}, 3]
    result = json.diff(src, dst)
    assert json.equals(result, [{'op': 'replace', 'path': '/1/a', 'value': 4}])


def test_patch_example():
    data = [1, {'a': 2}, 3]
    d = [{'op': 'replace', 'path': '/1/a', 'value': 4}]
    result = json.patch(data, d)
    assert json.equals(result, [1, {'a': 4}, 3])
