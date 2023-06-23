"""JSON Schema repository"""

import importlib.resources
import itertools
import pathlib
import typing
import urllib.parse
import weakref

from hat.json.data import Data
from hat.json.encoder import decode_file
from hat.json.validator import DefaultValidator, Validator


class SchemaRepository:
    """JSON Schema repository.

    A repository that holds json schemas and enables validation against them.

    Repository can be initialized with multiple arguments, which can be
    instances of ``pathlib.PurePath``, ``Data`` or ``SchemaRepository``.

    If an argument is of type ``pathlib.PurePath``, and path points to file
    with a suffix '.json', '.yml' or '.yaml', json serializable data is decoded
    from the file. Otherwise, it is assumed that path points to a directory,
    which is recursively searched for json and yaml files. All decoded schemas
    are added to the repository. If a schema with the same `id` was previously
    added, an exception is raised.

    If an argument is of type ``Data``, it should be a json serializable data
    representation of a JSON schema. If a schema with the same `id` was
    previously added, an exception is raised.

    If an argument is of type ``SchemaRepository``, its schemas are added to
    the new repository. Previously added schemas with the same `id` are
    replaced.

    """

    def __init__(self, *args: typing.Union[pathlib.PurePath,
                                           Data,
                                           'SchemaRepository']):
        self._validators = weakref.WeakValueDictionary()
        self._data = {}
        for arg in args:
            if isinstance(arg, pathlib.PurePath):
                self._load_path(arg)
            elif isinstance(arg, SchemaRepository):
                self._load_repository(arg)
            else:
                self._load_schema(arg)

    def get_uri_schemes(self) -> typing.Iterable[str]:
        """Get URI schemes stored in repository"""
        return self._data.keys()

    def get_schema_ids(self,
                       uri_schemes: typing.Iterable[str] | None = None
                       ) -> typing.Iterable[str]:
        """Get schema ids stored in repository

        If `uri_schemes` is ``None``, all schema ids are returned. Otherwise,
        only schema ids that have one of provided URI scheme are returned.

        """
        if uri_schemes is None:
            uri_schemes = self._data.keys()

        for uri_scheme in uri_schemes:
            schemas = self._data.get(uri_scheme)
            if not schemas:
                continue

            for path in schemas.keys():
                yield f'{uri_scheme}://{path}'

    def get_schema(self, schema_id: str) -> Data:
        """Get stored schema based on schema id"""
        uri = urllib.parse.urlparse(schema_id)
        path = uri.netloc + uri.path
        return self._data[uri.scheme][path]

    def validate(self,
                 schema_id: str,
                 data: Data,
                 validator_cls: typing.Type[Validator] = DefaultValidator):
        """Validate data against JSON schema.

        Args:
            schema_id: JSON schema identifier
            data: data to be validated
            validator_cls: validator implementation

        Raises:
            Exception

        """
        validator = self._validators.get(validator_cls)
        if validator is None:
            validator = validator_cls(self)
            self._validators[validator_cls] = validator

        validator.validate(schema_id, data)

    def to_json(self) -> Data:
        """Export repository content as json serializable data.

        Entire repository content is exported as json serializable data.
        New repository can be created from the exported content by using
        :meth:`SchemaRepository.from_json`.

        """
        return self._data

    @staticmethod
    def from_json(data: pathlib.PurePath | Data
                  ) -> 'SchemaRepository':
        """Create new repository from content exported as json serializable
        data.

        Creates a new repository from content of another repository that was
        exported by using :meth:`SchemaRepository.to_json`.

        Args:
            data: repository data

        """
        if isinstance(data, pathlib.PurePath):
            data = decode_file(data)
        repo = SchemaRepository()
        repo._data = data
        return repo

    def _load_path(self, path):
        json_suffixes = {'.json', '.yaml', '.yml'}
        paths = ([path] if path.suffix in json_suffixes
                 else list(itertools.chain.from_iterable(
                    path.rglob(f'*{i}') for i in json_suffixes)))
        for path in paths:
            schema = decode_file(path)
            self._load_schema(schema)

    def _load_schema(self, schema):
        if '$schema' in schema:
            meta_schema_id = urllib.parse.urldefrag(schema['$schema']).url
            if meta_schema_id not in _meta_schema_ids:
                schema = dict(schema)
                del schema['$schema']

        uri = urllib.parse.urlparse(schema['id'])
        path = uri.netloc + uri.path
        if uri.scheme not in self._data:
            self._data[uri.scheme] = {}
        if path in self._data[uri.scheme]:
            raise Exception(f"duplicate schema id {uri.scheme}://{path}")
        self._data[uri.scheme][path] = schema

    def _load_repository(self, repo):
        for k, v in repo._data.items():
            if k not in self._data:
                self._data[k] = v
            else:
                self._data[k].update(v)


_meta_schema_ids = {"http://json-schema.org/draft-03/schema",
                    "http://json-schema.org/draft-04/schema",
                    "http://json-schema.org/draft-06/schema",
                    "http://json-schema.org/draft-07/schema",
                    "https://json-schema.org/draft/2019-09/schema",
                    "https://json-schema.org/draft/2020-12/schema"}


try:
    with importlib.resources.as_file(importlib.resources.files(__package__) /
                                     'json_schema_repo.json') as _p:
        json_schema_repo: SchemaRepository = SchemaRepository.from_json(_p)
        """JSON Schema repository with generic schemas"""

except FileNotFoundError:
    json_schema_repo = SchemaRepository()
