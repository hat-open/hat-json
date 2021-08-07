from hat.doit import common
from src_doit import *  # NOQA

DOIT_CONFIG = common.init(python_paths=['src_py'],
                          default_tasks=['build'])
