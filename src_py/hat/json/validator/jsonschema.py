import urllib.parse

import jsonschema.validators

from hat.json.data import Data
from hat.json.validator.common import Repository


class JsonSchemaValidator:

    def __init__(self, repo: Repository):
        self._repo = repo

    def validate(self, schema_id: str, data: Data):
        uri = urllib.parse.urlparse(schema_id)
        path = uri.netloc + uri.path
        resolver = jsonschema.RefResolver(
            base_uri=f'{uri.scheme}://{path}',
            referrer=self._repo.get_schema(schema_id),
            handlers={i: self._repo.get_schema
                      for i in self._repo.get_uri_schemes()})
        jsonschema.validate(
            instance=data,
            schema=resolver.resolve_fragment(resolver.referrer, uri.fragment),
            resolver=resolver)
