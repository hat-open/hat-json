import pathlib

import pytest

from hat import json


@pytest.mark.parametrize('format', list(json.Format))
@pytest.mark.parametrize('indent', [None, 4])
@pytest.mark.parametrize('data', [
    None,
    True,
    False,
    1,
    1.0,
    'abc',
    [1, 2, 3],
    {'a': [[], [1], 'abc', True, [1, 1.0]]}
])
def test_encode_decode(format, indent, data):
    if format == json.Format.TOML and not isinstance(data, dict):
        return

    encoded = json.encode(data, format, indent)
    decoded = json.decode(encoded, format)
    assert data == decoded


@pytest.mark.parametrize('path, format', [
    ('abc.json', json.Format.JSON),
    ('abc.yaml', json.Format.YAML),
    ('abc.yml', json.Format.YAML),
    ('abc.toml', json.Format.TOML)
])
def test_get_file_format_valid(path, format):
    result = json.get_file_format(pathlib.Path(path))
    assert result == format


@pytest.mark.parametrize('path', [
    'abc',
    'abc.JSON',
    'abc.xyz'
])
def test_get_file_format_invalid(path):
    with pytest.raises(Exception):
        json.get_file_format(pathlib.Path(path))


@pytest.mark.parametrize('format', list(json.Format))
@pytest.mark.parametrize('indent', [None, 4])
@pytest.mark.parametrize('data', [
    None,
    True,
    False,
    1,
    1.0,
    'abc',
    [1, 2, 3],
    {'a': [[], [1], 'abc', True, [1, 1.0]]}
])
def test_encode_decode_file(tmp_path, format, indent, data):
    if format == json.Format.TOML and not isinstance(data, dict):
        return

    path = tmp_path / 'data'
    json.encode_file(data, path, format, indent)
    decoded = json.decode_file(path, format)
    assert data == decoded

    path = path.with_suffix(f'.{format.value}')
    json.encode_file(data, path, None, indent)
    decoded = json.decode_file(path, None)
    assert data == decoded
