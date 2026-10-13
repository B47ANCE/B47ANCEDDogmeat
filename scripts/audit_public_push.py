"""Inspect staged AND tracked content before public push; never print suspected secrets."""
from pathlib import PurePosixPath
import json
import re
import subprocess
import sys


def git(*args):
    return subprocess.check_output(['git', *args])


def main():
    staged = git('diff', '--cached', '--name-only', '-z').decode().split('\0')
    tracked = git('ls-files', '-z').decode().split('\0')
    paths = sorted(set(filter(None, staged + tracked)))
    forbidden_parts = {'research','.m0r-local','.agents','.codex','dist','staging','logs','diagnostics','.ssh'}
    forbidden_suffixes = {'.jar','.class','.java','.zip','.log','.pem','.key','.pfx','.ppk','.dmp'}
    patterns = [rb'gh[pousr]_[A-Za-z0-9]{20,}', rb'github_pat_[A-Za-z0-9_]{20,}',
                rb'-----BEGIN [A-Z ]*PRIVATE KEY-----',
                rb'(?i)(?:password|token|secret)\s*[:=]\s*[\x22\x27][^\x22\x27]{8,}[\x22\x27]',
                rb'AKIA[0-9A-Z]{16}']
    findings=[]
    case_map={}
    for path in paths:
        p=PurePosixPath(path)
        if p.is_absolute() or '..' in p.parts or set(p.parts)&forbidden_parts or p.suffix.lower() in forbidden_suffixes or p.name in ('local.settings.json','.env','server-console.txt','console.txt'):
            findings.append({'path':path,'reason':'Excluded/generated/native/private file path'})
            continue
        if path.casefold() in case_map and case_map[path.casefold()]!=path:
            findings.append({'path':path,'reason':'Filename case collision'})
        case_map[path.casefold()]=path
        try:
            content=git('show', ':'+path)
        except subprocess.CalledProcessError:
            findings.append({'path':path,'reason':'Index content unavailable; inspect deletion explicitly'})
            continue
        if any(re.search(pattern,content) for pattern in patterns):
            findings.append({'path':path,'reason':'Suspected credential/private-key content; value withheld'})
    print(json.dumps({'status':'PASS' if not findings else 'STOP','staged_paths':len(list(filter(None,staged))),
                      'tracked_and_staged_files_audited':len(paths),'findings':findings,
                      'scope':'Path/case and targeted secret patterns; human diff review still required'},indent=2))
    return bool(findings)


if __name__=='__main__':
    sys.exit(main())
