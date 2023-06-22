"""JSON Data encoder/decoder"""

import enum
import io
import json
import pathlib

import tomli
import tomli_w
import yaml

from hat.json.data import Data


class Format(enum.Enum):
    """Encoding format"""
    JSON = 'json'
    YAML = 'yaml'
    TOML = 'toml'


def encode(data: Data,
           format: Format = Format.JSON,
           indent: int | None = None
           ) -> str:
    """Encode JSON data.

    In case of TOML format, data must be JSON Object.

    Args:
        data: JSON data
        format: encoding format
        indent: indentation size

    """
    if format == Format.JSON:
        return json.dumps(data, indent=indent, allow_nan=False)

    if format == Format.YAML:
        dumper = (yaml.CSafeDumper if hasattr(yaml, 'CSafeDumper')
                  else yaml.SafeDumper)
        return str(yaml.dump(data, indent=indent, Dumper=dumper))

    if format == Format.TOML:
        return tomli_w.dumps(data)

    raise ValueError('unsupported format')


def decode(data_str: str,
           format: Format = Format.JSON
           ) -> Data:
    """Decode JSON data.

    Args:
        data_str: encoded JSON data
        format: encoding format

    """
    if format == Format.JSON:
        return json.loads(data_str)

    if format == Format.YAML:
        loader = (yaml.CSafeLoader if hasattr(yaml, 'CSafeLoader')
                  else yaml.SafeLoader)
        return yaml.load(io.StringIO(data_str), Loader=loader)

    if format == Format.TOML:
        return tomli.loads(data_str)

    raise ValueError('unsupported format')


def get_file_format(path: pathlib.PurePath) -> Format:
    """Detect file format based on path suffix"""
    if path.suffix == '.json':
        return Format.JSON

    if path.suffix in ('.yaml', '.yml'):
        return Format.YAML

    if path.suffix == '.toml':
        return Format.TOML

    raise ValueError('can not determine format from path suffix')


def encode_file(data: Data,
                path: pathlib.PurePath,
                format: Format | None = None,
                indent: int | None = 4):
    """Encode JSON data to file.

    If `format` is ``None``, encoding format is derived from path suffix.

    In case of TOML format, data must be JSON Object.

    Args:
        data: JSON data
        path: file path
        format: encoding format
        indent: indentation size

    """
    if format is None:
        format = get_file_format(path)

    flags = 'w' if format != Format.TOML else 'wb'
    encoding = 'utf-8' if format != Format.TOML else None

    with open(path, flags, encoding=encoding) as f:
        encode_stream(data, f, format, indent)


def decode_file(path: pathlib.PurePath,
                format: Format | None = None
                ) -> Data:
    """Decode JSON data from file.

    If `format` is ``None``, encoding format is derived from path suffix.

    Args:
        path: file path
        format: encoding format

    """
    if format is None:
        format = get_file_format(path)

    flags = 'r' if format != Format.TOML else 'rb'
    encoding = 'utf-8' if format != Format.TOML else None

    with open(path, flags, encoding=encoding) as f:
        return decode_stream(f, format)


def encode_stream(data: Data,
                  stream: io.TextIOBase | io.RawIOBase,
                  format: Format = Format.JSON,
                  indent: int | None = 4):
    """Encode JSON data to stream.

    In case of TOML format, data must be JSON Object.

    In case of TOML format, `stream` should be `io.RawIOBase`. For
    other formats, `io.TextIOBase` is expected.

    Args:
        data: JSON data
        stream: output stream
        format: encoding format
        indent: indentation size

    """
    if format == Format.JSON:
        json.dump(data, stream, indent=indent, allow_nan=False)

    elif format == Format.YAML:
        dumper = (yaml.CSafeDumper if hasattr(yaml, 'CSafeDumper')
                  else yaml.SafeDumper)
        yaml.dump(data, stream, indent=indent, Dumper=dumper,
                  explicit_start=True, explicit_end=True)

    elif format == Format.TOML:
        tomli_w.dump(data, stream)

    else:
        raise ValueError('unsupported format')


def decode_stream(stream: io.TextIOBase | io.RawIOBase,
                  format: Format = Format.JSON
                  ) -> Data:
    """Decode JSON data from stream.

    In case of TOML format, `stream` should be `io.RawIOBase`. For
    other formats, `io.TextIOBase` is expected.

    Args:
        stream: input stream
        format: encoding format

    """
    if format == Format.JSON:
        return json.load(stream)

    if format == Format.YAML:
        loader = (yaml.CSafeLoader if hasattr(yaml, 'CSafeLoader')
                  else yaml.SafeLoader)
        return yaml.load(stream, Loader=loader)

    if format == Format.TOML:
        return tomli.load(stream)

    raise ValueError('unsupported format')
