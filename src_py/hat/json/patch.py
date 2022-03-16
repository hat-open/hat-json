"""JSON Patch"""

import jsonpatch

from hat.json.data import Data


def diff(src: Data,
         dst: Data
         ) -> Data:
    """Generate JSON Patch diff.

    Example::

        src = [1, {'a': 2}, 3]
        dst = [1, {'a': 4}, 3]
        result = diff(src, dst)
        assert result == [{'op': 'replace', 'path': '/1/a', 'value': 4}]

    """
    return jsonpatch.JsonPatch.from_diff(src, dst).patch


def patch(data: Data,
          diff: Data
          ) -> Data:
    """Apply JSON Patch diff.

    Example::

        data = [1, {'a': 2}, 3]
        d = [{'op': 'replace', 'path': '/1/a', 'value': 4}]
        result = patch(data, d)
        assert result == [1, {'a': 4}, 3]

    """
    return jsonpatch.apply_patch(data, diff)


# check upstream changes in jsonpatch and validate performance impact

# def _monkeypatch_jsonpatch():
#     """Monkeypatch jsonpatch.

#     Patch incorrect value comparison between ``bool`` and numeric values when
#     diffing json serializable data.

#     Comparing `False` to `0` or `0.0`; and `True` to `1` or `1.0` incorrectly
#     results in no change.

#     """
#     def _compare_values(self, path, key, src, dst):

#         if isinstance(src, jsonpatch.MutableMapping) and \
#                 isinstance(dst, jsonpatch.MutableMapping):
#             self._compare_dicts(jsonpatch._path_join(path, key), src, dst)

#         elif isinstance(src, jsonpatch.MutableSequence) and \
#                 isinstance(dst, jsonpatch.MutableSequence):
#             self._compare_lists(jsonpatch._path_join(path, key), src, dst)

#         elif isinstance(src, bool) == isinstance(dst, bool) and src == dst:
#             pass

#         else:
#             self._item_replaced(path, key, dst)

#     jsonpatch.DiffBuilder._compare_values = _compare_values


# _monkeypatch_jsonpatch()
