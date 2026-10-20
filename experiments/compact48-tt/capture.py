#!/usr/bin/env python3
"""Capture complete exact62/own-PGO TT producers, consumers and allocation paths."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

B = Path('/home/legolas/rook2-experiments/compact48-tt-20261020-01')
CONTROL = Path('/home/legolas/rook2-experiments/original-worktree/evidence/exttsp-profiled-pgo-use-build-20261020-01/rook2-exact')
H = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert os.sched_getaffinity(0) == H
    candidate = json.loads((B / 'use-build/frozen-image.json').read_text())
    assert sha(CONTROL) == '01237e6dfe89822e540d0f07c7b70f7227537a846ce8c69ea9e91167b759e98d'
    assert sha(Path(candidate['path'])) == candidate['sha256']
    out = B / 'capture'
    out.mkdir()
    receipt = {'engine_runs': 0, 'images': {}, 'tool_hashes': {}}
    for tool in ('nm', 'objdump', 'readelf'):
        receipt['tool_hashes'][tool] = sha(Path('/usr/bin') / tool)
    for label, image in [('control', CONTROL), ('candidate', Path(candidate['path']))]:
        before = sha(image)
        directory = out / label
        directory.mkdir()
        commands = {
            'nm.txt': ['/usr/bin/nm', '-S', '-C', '--defined-only', str(image)],
            'full.disassembly': ['/usr/bin/objdump', '-d', '-w', '-C', '-Mintel', '--no-show-raw-insn', str(image)],
            'sections.txt': ['/usr/bin/readelf', '-SW', str(image)],
            'relocations.txt': ['/usr/bin/readelf', '-rW', str(image)],
        }
        for name, command in commands.items():
            with (directory / name).open('xb') as stdout, (directory / (name + '.stderr')).open('xb') as stderr:
                child = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=30)
            assert child.returncode == 0 and not (directory / (name + '.stderr')).stat().st_size
        symbols = []
        for line in (directory / 'nm.txt').read_text().splitlines():
            m = re.fullmatch(r'([0-9a-f]+) ([0-9a-f]+) ([A-Za-z]) (.+)', line)
            if m:
                symbols.append(dict(address=int(m[1], 16), size=int(m[2], 16), type=m[3], name=m[4]))
        assembly = (directory / 'full.disassembly').read_text()
        starts = list(re.finditer(r'^([0-9a-f]+) <(.+)>:\n', assembly, re.M))
        blocks = {int(m[1], 16): assembly[m.start():starts[i+1].start() if i+1<len(starts) else None]
                  for i, m in enumerate(starts)}
        selected = []
        for s in symbols:
            if s['type'] not in ('t', 'T'):
                continue
            name = s['name']
            if (any(prefix in name for prefix in ('rook2::remembered::', 'rook2::ordinary::',
                    'rook2::engine::', 'rook2::session::', 'rook2::timed::', 'rook2::timed_sequence::'))
                or name in ('rook2::run', '__rust_alloc', '__rust_alloc_zeroed', '__rust_dealloc', '__rust_realloc')
                or 'RawVecInner' in name or ('Vec<' in name and 'Group' in name)):
                p = directory / ('owner-' + format(s['address'], 'x') + '.asm')
                p.write_text(blocks[s['address']])
                selected.append({**s, 'capture': str(p), 'capture_sha256': sha(p)})
        assert sha(image) == before
        receipt['images'][label] = dict(path=str(image), sha256=before, bytes=image.stat().st_size,
                                       selected_owners=selected, commands=commands,
                                       captures_sha256={p.name: sha(p) for p in directory.iterdir()})
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({'engine_runs': 0, 'owners': {k: v['selected_owners']
                                                   for k, v in receipt['images'].items()}}))


if __name__ == '__main__':
    main()
