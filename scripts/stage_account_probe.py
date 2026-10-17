"""Assemble an explicit disposable account probe; never install, launch or archive."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from build_loadable import assemble, sources, ROOT

PROBE = ROOT / 'tests/runtime/account_binding'


def stage(destination):
    result = assemble(destination)
    mapping = {f'42/media/lua/{p.relative_to(PROBE).as_posix()}': p for p in PROBE.rglob('*.lua')}
    expected = set(sources()) | set(mapping)
    if len(mapping) != 3 or len(expected) != len(sources()) + 3:
        raise ValueError('Unexpected probe inventory or production collision')
    for relative, source in mapping.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    actual = {p.relative_to(destination).as_posix() for p in destination.rglob('*') if p.is_file()}
    if actual != expected or any((destination / p).read_bytes() != s.read_bytes() for p, s in mapping.items()):
        raise ValueError('Disposable probe assembly differs')
    result.update(status='DISPOSABLE PROBE SOURCE PARITY PASS', files=len(actual), probe_files=3,
                  ownership='DISABLED', live_tasks='DISABLED', runtime='NOT TESTED')
    result['probe_hashes'] = {p: hashlib.sha256(s.read_bytes()).hexdigest() for p, s in mapping.items()}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true')
    group.add_argument('--output', type=Path, help='New tree beneath ignored .m0r-local only')
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory(prefix='b47dog-account-probe-') as directory:
            result = stage(Path(directory) / 'B47ANCEDDogmeat')
    else:
        destination = args.output.resolve()
        if not destination.is_relative_to(ROOT / '.m0r-local'):
            parser.error('Explicit staging must remain beneath ignored .m0r-local')
        result = stage(destination)
        result['output'] = str(destination)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
