#!/usr/bin/env python3
"""Strict, non-destructive BBCode renderer for canonical Workshop description Markdown."""
import argparse, re, subprocess, sys
from pathlib import Path

def github_url(repo):
    p = subprocess.run(['git','-C',str(repo),'remote','get-url','origin'], capture_output=True,text=True)
    if p.returncode: raise ValueError('Git origin unavailable')
    s=p.stdout.strip()
    m=re.fullmatch(r'(?:git@github\.com:|ssh://git@github\.com/|https://github\.com/)([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?',s)
    if not m: raise ValueError('Git origin is not a supported GitHub URL')
    return 'https://github.com/'+m[1]+'/'+m[2]

def render(src, url):
    if '{{' in src or '}}' in src or re.search(r'(?im)\b(?:TODO|TBD|PLACEHOLDER)\b',src):
        raise ValueError('Description contains template placeholders')
    if re.search(r'(?m)^\s*(?:<|```|!\[|\||>)',src):
        raise ValueError('Unsupported markup: review and convert manually')
    required=['Overview','Features','Compatibility & Requirements','Source Code & Development','Credits & Permissions']
    for name in required:
        if not re.search(r'(?m)^## '+re.escape(name)+r'\s*$',src): raise ValueError('Missing section: '+name)
    src=re.sub(r'(?m)^GitHub:[^\S\r\n]*\S+[^\S\r\n]*$',f'GitHub: {url}',src)
    if not re.search(r'(?m)^GitHub:\s*',src): raise ValueError('Missing GitHub line')
    lines=[]
    for line in src.splitlines():
        if re.search(r'\[[^]]+\]\([^)]+\)|\*\*|`',line): raise ValueError('Unsupported inline Markdown: '+line)
        if line.startswith('# '): line='[size=large][b]'+line[2:]+'[/b][/size]'
        elif line.startswith('## '): line='[b]'+line[3:]+'[/b]'
        elif line.startswith('- '): line='• '+line[2:]
        elif line.startswith('GitHub: '): line='[url='+url+']GitHub — Source Code & Issues[/url]'
        elif re.search(r'\[[^]]+\]\([^)]+\)|\*\*|`',line): raise ValueError('Unsupported inline Markdown: '+line)
        lines.append(line)
    output='\n'.join(lines).strip()+'\n'
    if '\\n' in output: raise ValueError('Literal escaped newline found')
    return output

def main():
    a=argparse.ArgumentParser();a.add_argument('--repo',type=Path,required=True);a.add_argument('--input',type=Path,required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--check',action='store_true');args=a.parse_args()
    try:
        url=github_url(args.repo); content=render(args.input.read_text(encoding='utf-8'),url)
        if args.check:
            if not args.output.is_file() or args.output.read_text(encoding='utf-8')!=content: raise ValueError('Generated output missing or stale')
        else:
            args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(content,encoding='utf-8',newline='\n')
        print('PASS: '+url)
    except (ValueError,OSError) as e:
        print('BLOCKED: '+str(e),file=sys.stderr);return 1
    return 0
if __name__=='__main__':sys.exit(main())
