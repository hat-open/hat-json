import pytest

from hat import json


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
    assert result == diff


def test_diff_example():
    src = [1, {'a': 2}, 3]
    dst = [1, {'a': 4}, 3]
    result = json.diff(src, dst)
    assert result == [{'op': 'replace', 'path': '/1/a', 'value': 4}]


def test_patch_example():
    data = [1, {'a': 2}, 3]
    d = [{'op': 'replace', 'path': '/1/a', 'value': 4}]
    result = json.patch(data, d)
    assert result == [1, {'a': 4}, 3]
