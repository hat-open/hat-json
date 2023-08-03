from pathlib import Path

from hat.doit import common
from hat.doit.py import (get_task_build_wheel,
                         get_task_run_pytest,
                         run_flake8)
from hat.doit.docs import (build_sphinx,
                           build_pdoc)

from hat import json


__all__ = ['task_clean_all',
           'task_build',
           'task_check',
           'task_test',
           'task_docs',
           'task_json_schema_repo']


build_dir = Path('build')
src_py_dir = Path('src_py')
pytest_dir = Path('test_pytest')
docs_dir = Path('docs')
schemas_json_dir = Path('schemas_json')

build_py_dir = build_dir / 'py'
build_docs_dir = build_dir / 'docs'
json_schema_repo_path = src_py_dir / 'hat/json/json_schema_repo.json'


def task_clean_all():
    """Clean all"""
    return {'actions': [(common.rm_rf, [build_dir,
                                        json_schema_repo_path])]}


def task_build():
    """Build"""
    return get_task_build_wheel(src_dir=src_py_dir,
                                build_dir=build_py_dir,
                                task_dep=['json_schema_repo'])


def task_check():
    """Check with flake8"""
    return {'actions': [(run_flake8, [src_py_dir]),
                        (run_flake8, [pytest_dir])]}


def task_test():
    """Test"""
    return get_task_run_pytest()


def task_docs():
    """Docs"""

    def build():
        build_sphinx(src_dir=docs_dir,
                     dst_dir=build_docs_dir,
                     project='hat-json')
        build_pdoc(module='hat.json',
                   dst_dir=build_docs_dir / 'py_api')

    return {'actions': [build]}


def task_json_schema_repo():
    """Generate JSON Schema Repository"""
    src_paths = list(schemas_json_dir.rglob('*.yaml'))

    def generate():
        repo = json.SchemaRepository(*src_paths)
        data = repo.to_json()
        json.encode_file(data, json_schema_repo_path, indent=None)

    return {'actions': [generate],
            'file_dep': src_paths,
            'targets': [json_schema_repo_path]}
