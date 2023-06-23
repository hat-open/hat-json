"""JSON Schema validator common structures"""

import typing

from hat.json.data import Data


class Repository(typing.Protocol):

    def get_uri_schemes(self) -> typing.Iterable[str]:
        """Get URI schemes stored in repository"""

    def get_schema_ids(self,
                       uri_schemes: typing.Iterable[str] | None = None
                       ) -> typing.Iterable[str]:
        """Get schema ids stored in repository

        If `uri_schemes` is ``None``, all schema ids are returned. Otherwise,
        only schema ids that have one of provided URI scheme are returned.

        """

    def get_schema(self, schema_id: str) -> Data:
        """Get stored schema based on schema id"""


class Validator(typing.Protocol):
    """JSON Schema validator interface

    Args:
        repo: repository containing JSON Schemas

    """

    def __init__(self, repo: Repository):
        ...

    def validate(self, schema_id: str, data: Data):
        """Validate data against JSON Schema.

        Args:
            schema_id: JSON schema identifier
            data: data to be validated

        Raises:
            Exception

        """
