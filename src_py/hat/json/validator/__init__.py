"""JSON Schema validators"""

from hat.json.validator.common import Validator
from hat.json.validator.jsonschema import JsonSchemaValidator


DefaultValidator = JsonSchemaValidator


__all__ = ['Validator',
           'DefaultValidator',
           'JsonSchemaValidator']
