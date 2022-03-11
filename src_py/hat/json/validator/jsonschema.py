import urllib.parse

import jsonschema.validators

from hat.json.data import Data


class JsonSchemaValidator:

    def __init__(self, repo: Data):
        self._repo = repo

    def validate(self, schema_id: str, data: Data):
        uri = urllib.parse.urlparse(schema_id)
        path = uri.netloc + uri.path
        resolver = jsonschema.RefResolver(
            base_uri=f'{uri.scheme}://{path}',
            referrer=self._repo[uri.scheme][path],
            handlers={i: self._get_schema
                      for i in self._repo.keys()})
        jsonschema.validate(
            instance=data,
            schema=resolver.resolve_fragment(resolver.referrer, uri.fragment),
            resolver=resolver)

    def _get_schema(self, schema_id):
        uri = urllib.parse.urlparse(schema_id)
        path = uri.netloc + uri.path
        return self._repo[uri.scheme][path]
