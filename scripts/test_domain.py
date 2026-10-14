"""Run actual Lua 5.1 offline tests; no Project Zomboid or save access."""
from pathlib import Path
import json
import platform
import sys

import lupa
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]


def main():
    lua = LuaRuntime(unpack_returned_tuples=True, register_eval=False, register_builtins=False)
    lua.globals().package.path = str(ROOT / 'src/domain/?.lua').replace('\\', '/')
    lua.globals().package.cpath = ''
    result = lua.execute((ROOT / 'tests/lua/ownership_spec.lua').read_text(encoding='utf-8'))
    output = {'project_version': (ROOT / 'VERSION').read_text(encoding='utf-8').strip(),
              'environment': platform.system() + ' offline ' + lua.eval('_VERSION') + ' through Lupa; not PZ/Kahlua',
              'lupa_version': lupa.__version__,
              'passed': result['passed'], 'failed': result['failed'],
              'failures': list(result['failures'].values()),
              'G6': 'NOT TESTED', 'G7': 'BLOCKED / NOT TESTED', 'G8': 'BLOCKED'}
    print(json.dumps(output, indent=2))
    return bool(result['failed'])


if __name__ == '__main__':
    sys.exit(main())
