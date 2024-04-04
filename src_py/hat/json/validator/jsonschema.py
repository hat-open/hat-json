import jsonschema
import referencing.exceptions

from hat.json.data import Data
from hat.json.validator.common import Repository


class JsonSchemaValidator:

    def __init__(self, repo: Repository):
        self._repo = repo
        self._registry = referencing.Registry(retrieve=self._retrieve)

    def validate(self, schema_id: str, data: Data):
        jsonschema.validate(instance=data,
                            schema={'$ref': schema_id},
                            registry=self._registry)

    def _retrieve(self, uri):
        try:
            schema = self._repo.get_schema(uri)

        except Exception:
            raise referencing.exceptions.NoSuchResource(uri)

        if '$schema' not in schema:
            schema = {
                **schema,
                '$schema': "https://json-schema.org/draft/2020-12/schema"}

        return referencing.Resource.from_contents(schema)
