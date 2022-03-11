import typing

from hat.json.data import Data


class Validator(typing.Protocol):

    def __init__(self, repo: Data):
        ...

    def validate(self, schema_id: str, data: Data):
        ...
