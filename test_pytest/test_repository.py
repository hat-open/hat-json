import pytest

from hat import json


validator_classes = [json.JsonSchemaValidator]


def test_schema_repository_init_empty():
    repo = json.SchemaRepository()
    assert not repo.to_json()


def test_schema_repository_init():
    schema = json.decode("id: 'xyz://abc'", format=json.Format.YAML)
    repo = json.SchemaRepository(schema)
    assert repo.to_json()


def test_schema_repository_init_duplicate_id():
    schema = json.decode("id: 'xyz://abc'", format=json.Format.YAML)
    repo = json.SchemaRepository(schema)
    assert repo.to_json() == json.SchemaRepository(repo, repo).to_json()
    with pytest.raises(Exception):
        json.SchemaRepository(schema, schema)


def test_schema_repository_init_paths(tmp_path):
    dir_path = tmp_path / 'repo'
    json_path = dir_path / 'schema.json'
    yaml_path = dir_path / 'schema.yaml'

    dir_path.mkdir()
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write('{"id": "xyz1://abc1"}')
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write("id: 'xyz2://abc2'")
    repo1 = json.SchemaRepository(dir_path)
    repo2 = json.SchemaRepository(json_path, yaml_path)
    assert repo1.to_json() == repo2.to_json()


@pytest.mark.parametrize("validator_cls", validator_classes)
@pytest.mark.parametrize("schemas, schema_id, data", [
    ([r'''
        id: 'xyz://abc'
      '''],
     'xyz://abc#',
     None),

    ([r'''
        id: 'xyz://abc#'
      '''],
     'xyz://abc#',
     {'a': 'b'}),

    ([r'''
        id: 'xyz://abc#'
      '''],
     'xyz://abc',
     [1, 2, 3]),

    ([r'''
        id: 'xyz://abc1'
        type: object
        required:
            - a
            - c
        properties:
            a:
                '$ref': 'xyz://abc2#/definitions/value'
            c:
                '$ref': 'xyz://abc2'
      ''',
      r'''
        id: 'xyz://abc2'
        type: integer
        definitions:
            value:
                type: string
      '''],
     'xyz://abc1',
     {'a': 'b', 'c': 1})
])
def test_json_schema_repository_validate(validator_cls, schemas, schema_id,
                                         data):
    repo = json.SchemaRepository(*[json.decode(i, format=json.Format.YAML)
                                   for i in schemas])
    repo.validate(schema_id, data,
                  validator_cls=validator_cls)


@pytest.mark.parametrize("validator_cls", validator_classes)
@pytest.mark.parametrize("schemas, schema_id, data", [
    ([r'''
        id: 'xyz://abc'
        type: integer
      '''],
     'xyz://abc',
     None)
])
def test_json_schema_repository_validate_invalid(validator_cls, schemas,
                                                 schema_id, data):
    repo = json.SchemaRepository(*[json.decode(i, format=json.Format.YAML)
                                   for i in schemas])
    with pytest.raises(Exception):
        repo.validate(schema_id, data,
                      validator_cls=validator_cls)


@pytest.mark.parametrize("validator_cls", validator_classes)
def test_json_schema_repository_invalid_meta_schema(validator_cls):
    schema = {'$schema': 'http://invalid',
              'id': 'xyz://abc',
              'type': 'integer'}
    repo = json.SchemaRepository(schema)

    repo.validate(schema['id'], 123,
                  validator_cls=validator_cls)

    with pytest.raises(Exception):
        repo.validate(schema['id'], 123.45,
                      validator_cls=validator_cls)
