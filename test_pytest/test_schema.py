import pytest

from hat import json


validator_classes = [json.PySchemaValidator,
                     json.RsSchemaValidator]


def test_create_schema_repository_empty():
    repo = json.create_schema_repository()
    assert repo == {}


def test_create_schema_repository():
    schema = json.decode("$id: 'xyz://abc'", format=json.Format.YAML)
    repo = json.create_schema_repository(schema)
    assert len(repo) == 1
    assert 'xyz://abc' in repo


def test_create_schema_repository_duplicate_id():
    schema = json.decode("id: 'xyz://abc'", format=json.Format.YAML)
    with pytest.raises(Exception):
        json.create_schema_repository(schema, schema)


def test_create_schema_repository_paths(tmp_path):
    dir_path = tmp_path / 'repo'
    json_path = dir_path / 'schema.json'
    yaml_path = dir_path / 'schema.yaml'

    dir_path.mkdir()
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write('{"$id": "xyz1://abc1"}')
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write("$id: 'xyz2://abc2'")
    repo1 = json.create_schema_repository(dir_path)
    repo2 = json.create_schema_repository(json_path, yaml_path)
    assert repo1 == repo2


def test_merge_schema_repositories():
    schema1 = json.decode("$id: 'xyz://abc'", format=json.Format.YAML)
    schema2 = json.decode("$id: 'xyz://cba'", format=json.Format.YAML)

    repo = json.merge_schema_repositories(
        json.create_schema_repository(schema1),
        json.create_schema_repository(schema2))

    assert len(repo) == 2
    assert 'xyz://abc' in repo
    assert 'xyz://cba' in repo


def test_merge_schema_repositories_conflict():
    schema1 = json.decode("$id: 'xyz://abc'", format=json.Format.YAML)
    schema2 = json.decode("$id: 'xyz://abc'\ntype: integer",
                          format=json.Format.YAML)

    repo1 = json.create_schema_repository(schema1)
    repo2 = json.create_schema_repository(schema2)

    repo = json.merge_schema_repositories(repo1, repo1)

    assert len(repo) == 1
    assert 'xyz://abc' in repo

    with pytest.raises(Exception):
        json.merge_schema_repositories(repo1, repo2)


@pytest.mark.parametrize("validator_cls", validator_classes)
@pytest.mark.parametrize("schemas, schema_id, data", [
    ([r'''
        $id: 'xyz://abc'
      '''],
     'xyz://abc',
     None),

    ([r'''
        id: 'xyz://abc#'
      '''],
     'xyz://abc',
     {'a': 'b'}),

    ([r'''
        $id: 'xyz://abc#'
      '''],
     'xyz://abc',
     [1, 2, 3]),

    ([r'''
        $id: 'xyz://abc1'
        type: object
        required:
            - a
            - c
        properties:
            a:
                '$ref': 'xyz://abc2#/$defs/value'
            c:
                '$ref': 'xyz://abc2'
            d:
                '$ref': '#/properties/a'
      ''',
      r'''
        $id: 'xyz://abc2'
        type: integer
        $defs:
            value:
                type: string
      '''],
     'xyz://abc1',
     {'a': 'b', 'c': 1, 'd': 'e'}),

    ([r'''
        $id: 'xyz://abc'
        type: array
        items:
            $ref: 'xyz://abc#/$defs/item'
        $defs:
            item:
                type: integer
      '''],
     'xyz://abc',
     [1, 2, 3]),

    ([r'''
        $id: 'xyz://abc'
        type: string
        $defs:
            item:
                type: integer
      '''],
     'xyz://abc#/$defs/item',
     123),
])
def test_json_schema_repository_validate(validator_cls, schemas, schema_id,
                                         data):
    repo = json.create_schema_repository(
        *(json.decode(i, format=json.Format.YAML) for i in schemas))
    validator = validator_cls(repo)
    validator.validate(schema_id, data)


@pytest.mark.parametrize("validator_cls", validator_classes)
@pytest.mark.parametrize("schemas, schema_id, data", [
    ([r'''
        $id: 'xyz://abc'
        type: integer
      '''],
     'xyz://abc',
     None)
])
def test_json_schema_repository_validate_invalid(validator_cls, schemas,
                                                 schema_id, data):
    repo = json.create_schema_repository(
        *(json.decode(i, format=json.Format.YAML) for i in schemas))
    validator = validator_cls(repo)
    with pytest.raises(Exception):
        validator.validate(schema_id, data)


@pytest.mark.parametrize("validator_cls", validator_classes)
def test_json_schema_repository_invalid_meta_schema(validator_cls):
    schema = {'$schema': 'http://invalid',
              '$id': 'xyz://abc',
              'type': 'integer'}

    with pytest.raises(Exception):
        json.create_schema_repository(schema)
