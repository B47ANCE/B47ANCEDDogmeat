"""Run actual Lua 5.1 offline tests; no Project Zomboid or save access."""
from pathlib import Path
import json
import platform
import sys
import tempfile

import lupa
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]


def runtime(directory):
    lua = LuaRuntime(unpack_returned_tuples=True, register_eval=False, register_builtins=False)
    lua.globals().package.path = ';'.join(str(ROOT / p).replace('\\', '/') for p in
                                         ('src/domain/?.lua', 'src/native/?.lua', 'src/bootstrap/shared/?.lua', 'tests/lua/?.lua',
                                          'tests/runtime/account_binding/shared/?.lua'))
    lua.globals().package.cpath = ''
    def target(relative):
        path = (directory / relative).resolve()
        if not path.is_relative_to(directory) or Path(relative).is_absolute():
            raise ValueError('Fixture path escaped disposable directory')
        return path
    def read_file(relative):
        path = target(relative)
        return path.read_text(encoding='ascii') if path.exists() else None
    def write_file(relative, data):
        path = target(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding='ascii', newline='')
    lua.globals().testfs_read = read_file
    lua.globals().testfs_write = write_file
    lua.globals().testfs_exists = lambda relative: target(relative).exists()
    lua.globals().test_bootstrap_server=(ROOT/'src/bootstrap/server/B47DogBootstrap.lua').read_text(encoding='utf-8')
    lua.globals().test_bootstrap_client=(ROOT/'src/bootstrap/client/B47DogTestMenu.lua').read_text(encoding='utf-8')
    lua.globals().test_account_probe_bootstrap=(ROOT/'tests/runtime/account_binding/server/B47AccountBindingProbeBootstrap.lua').read_text(encoding='utf-8')
    lua.globals().test_account_probe_client=(ROOT/'tests/runtime/account_binding/client/B47AccountBindingProbeClient.lua').read_text(encoding='utf-8')
    return lua


def main():
    suites = []
    syntax=runtime(Path(tempfile.gettempdir()).resolve())
    inventory=json.loads((ROOT/'source-inventory.json').read_text(encoding='utf-8'))
    compile_lua=syntax.eval('function(source) local fn,err=loadstring(source); assert(fn,err); return true end')
    for relative in inventory['authoritative_lua']:
        compile_lua((ROOT/relative).read_text(encoding='utf-8'))
    for path in (ROOT/'tests/runtime/account_binding').rglob('*.lua'):
        compile_lua(path.read_text(encoding='utf-8'))
    del syntax
    with tempfile.TemporaryDirectory(prefix='b47dog-offline-') as temporary:
        directory = Path(temporary).resolve()
        for name, phase in [('ownership_spec.lua', None), ('storage_spec.lua', None), ('pairing_spec.lua', None),
                            ('provision_spec.lua', None), ('registration_spec.lua', None), ('bootstrap_spec.lua', None),
                            ('identity_authority_spec.lua', None),
                            ('admission_spec.lua', None),
                            ('continuity_spec.lua', None),
                            ('database_transaction_spec.lua', None),
                            ('account_binding_probe_spec.lua', None),
                            ('database_restart_spec.lua', 'prepare'), ('database_restart_spec.lua', 'recover'),
                            ('restart_spec.lua', 'prepare'), ('restart_spec.lua', 'recover'),
                            ('native_restart_spec.lua', 'prepare'), ('native_restart_spec.lua', 'recover'),
                            ('provision_restart_spec.lua', 'prepare'), ('provision_restart_spec.lua', 'recover'),
                            ('identity_restart_spec.lua', 'prepare'), ('identity_restart_spec.lua', 'recover'),
                            ('admission_restart_spec.lua', 'prepare'), ('admission_restart_spec.lua', 'recover'),
                            ('continuity_restart_spec.lua', 'prepare'), ('continuity_restart_spec.lua', 'recover'),
                            ('save_load_equivalence_spec.lua', 'honest'), ('save_load_equivalence_spec.lua', 'copy')]:
            lua = runtime(directory)
            lua_version = lua.eval('_VERSION')
            lua.globals().RESTART_PHASE = phase
            result = lua.execute((ROOT / 'tests/lua' / name).read_text(encoding='utf-8'))
            suites.append({'suite': name + (':' + phase if phase else ''),
                           'passed': result['passed'], 'failed': result['failed'],
                           'failures': list(result['failures'].values())})
            del lua
    output = {'project_version': (ROOT / 'VERSION').read_text(encoding='utf-8').strip(),
              'environment': platform.system() + ' offline ' + lua_version + ' through Lupa; not PZ/Kahlua',
              'lupa_version': lupa.__version__,
              'passed': sum(s['passed'] for s in suites), 'failed': sum(s['failed'] for s in suites),
              'suites': suites, 'filesystem': 'Disposable real files; restart uses separate Lua VMs, not PZ/server processes',
              'G6': 'NOT TESTED', 'G7': 'BLOCKED / NOT TESTED', 'G8': 'BLOCKED'}
    print(json.dumps(output, indent=2))
    return bool(output['failed'])


if __name__ == '__main__':
    sys.exit(main())
