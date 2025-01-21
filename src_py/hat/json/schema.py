"""JSON Schema repository"""

import abc
import importlib.resources
import itertools
import pathlib
import typing
import urllib.parse

import jsonschema
import referencing.exceptions

from hat.json.data import Data, Object
from hat.json.encoder import decode_file

try:
    import jsonschema_rs

except ImportError:
    jsonschema_rs = None


SchemaId: typing.TypeAlias = str
"JSON Schema identifier"

Schema: typing.TypeAlias = Object
"""JSON Schema"""

SchemaRepository: typing.TypeAlias = dict[SchemaId, Schema]
"""JSON Schema repository"""


def create_schema_repository(*args: pathlib.PurePath | Schema
                             ) -> SchemaRepository:
    """Create JSON Schema repository.

    Repository can be initialized with multiple arguments, which can be
    instances of ``pathlib.PurePath`` or ``Schema``.

    If an argument is of type ``pathlib.PurePath``, and path points to file
    with a suffix '.json', '.yml' or '.yaml', json serializable data is decoded
    from the file. Otherwise, it is assumed that path points to a directory,
    which is recursively searched for json and yaml files. All decoded schemas
    are added to the repository. If a schema with the same `id` was previously
    added, an exception is raised.

    If an argument is of type ``Schema``, it should be a json serializable data
    representation of a JSON schema. If a schema with the same `id` was
    previously added, an exception is raised.

    """
    repo = {}

    for arg in args:
        if isinstance(arg, pathlib.PurePath):
            if arg.suffix in _schema_path_suffixes:
                paths = [arg]

            else:
                paths = itertools.chain.from_iterable(
                    arg.rglob(f'*{i}') for i in _schema_path_suffixes)

            schemas = (decode_file(path) for path in paths)

        elif isinstance(arg, dict):
            schemas = [arg]

        else:
            raise TypeError('invalid argument type')

        for schema in schemas:
            if '$schema' in schema:
                meta_schema_id = urllib.parse.urldefrag(schema['$schema']).url
                if meta_schema_id not in _meta_schema_ids:
                    raise Exception(
                        f"unsupported meta schema id {meta_schema_id}")

            else:
                schema = {'$schema': _default_meta_schema_id,
                          **schema}

            schema_id = schema.get('$id')
            if not schema_id:
                schema_id = schema.get('id')
            if not schema_id:
                raise Exception('invalid schema id')

            sanitized_schema_id = urllib.parse.urldefrag(schema_id).url
            if sanitized_schema_id in repo:
                raise Exception(f"duplicate schema id {sanitized_schema_id}")

            repo[sanitized_schema_id] = schema

    return repo


def merge_schema_repositories(*repos: SchemaRepository
                              ) -> SchemaRepository:
    """Merge JSON Schema repositories.

    Exception is raised is multiple repositories contain same schema id with
    diferent schemas.

    """
    result = {}

    for repo in repos:
        for schema_id, schema in repo.items():
            other_schema = result.get(schema_id)
            if other_schema is not None and other_schema != schema:
                raise Exception(f"conflict for schema id {schema_id}")

            result[schema_id] = schema

    return result


class SchemaValidator(abc.ABC):
    """JSON Schema validator interface

    Args:
        repo: repository containing JSON Schemas

    """

    @abc.abstractmethod
    def __init__(self, repo: SchemaRepository):
        pass

    @abc.abstractmethod
    def validate(self, schema_id: SchemaId, data: Data):
        """Validate data against JSON Schema.

        Args:
            schema_id: JSON schema identifier
            data: data to be validated

        Raises:
            Exception

        """


class PySchemaValidator(SchemaValidator):
    """Python implementation of SchemaValidator"""

    def __init__(self, repo: SchemaRepository):
        self._repo = repo
        self._registry = referencing.Registry(retrieve=self._retrieve)

    def validate(self, schema_id: SchemaId, data: Data):
        jsonschema.validate(instance=data,
                            schema={'$ref': schema_id},
                            registry=self._registry)

    def _retrieve(self, uri):
        try:
            schema = self._repo[uri]

        except KeyError:
            raise referencing.exceptions.NoSuchResource(uri)

        return referencing.Resource.from_contents(schema)


class RsSchemaValidator(SchemaValidator):
    """Rust implementation of SchemaValidatior"""

    def __init__(self, repo: SchemaRepository):
        if not jsonschema_rs:
            raise Exception('implementation not available')

        self._repo = repo
        self._defs = {i: {'$ref': i} for i in self._repo.keys()}

    def validate(self, schema_id: SchemaId, data: Data):
        jsonschema_rs.validate(schema={'$ref': schema_id,
                                       '$defs': self._defs},
                               instance=data,
                               retriever=self._retriever)

    def _retriever(self, uri):
        return self._repo[uri]


if jsonschema_rs:
    DefaultSchemaValidator: type[SchemaValidator] = RsSchemaValidator

else:
    DefaultSchemaValidator: type[SchemaValidator] = PySchemaValidator


try:
    with importlib.resources.as_file(importlib.resources.files(__package__) /
                                     'json_schema_repo.json') as _p:
        json_schema_repo: SchemaRepository = decode_file(_p)
        """JSON Schema repository with generic schemas"""

except FileNotFoundError:
    json_schema_repo = {}


_schema_path_suffixes = {'.json', '.yaml', '.yml'}

_meta_schema_ids = {"http://json-schema.org/draft-03/schema",
                    "http://json-schema.org/draft-04/schema",
                    "http://json-schema.org/draft-06/schema",
                    "http://json-schema.org/draft-07/schema",
                    "https://json-schema.org/draft/2019-09/schema",
                    "https://json-schema.org/draft/2020-12/schema"}

_default_meta_schema_id = "https://json-schema.org/draft/2020-12/schema"
