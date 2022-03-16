"""JSON Schema validator common structures"""

import typing

from hat.json.data import Data


class Validator(typing.Protocol):
    """JSON Schema validator interface

    Args:
        repo: repository containing JSON Schemas

    """

    def __init__(self, repo: 'hat.json.SchemaRepository'):  # NOQA
        ...

    def validate(self, schema_id: str, data: Data):
        """Validate data against JSON Schema.

        Args:
            schema_id: JSON schema identifier
            data: data to be validated

        Raises:
            Exception

        """
