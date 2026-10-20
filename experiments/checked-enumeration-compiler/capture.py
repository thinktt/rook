#!/usr/bin/env python3
"""Capture actual complete machine code; do not run either engine."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

B = Path('/home/legolas/rook2-experiments/checked-enumeration-compiler-20261020-01')
H = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert os.sched_getaffinity(0) == H
    out = B / 'capture'
    out.mkdir()
    control = json.loads((B / 'control-admission.json').read_text())
    candidate = json.loads((B / 'build/frozen-image.json').read_text())
    result = {'engines_run': 0, 'images': {}, 'tools': {}}
    for tool in ('nm', 'objdump', 'readelf'):
        result['tools'][tool] = sha(Path('/usr/bin/' + tool).resolve())
    for label, identity in [('control', control), ('candidate', candidate)]:
        image = Path(identity.get('path', identity.get('control')))
        expected = identity['sha256']
        assert sha(image) == expected
        directory = out / label
        directory.mkdir()
        commands = {
            'nm.txt': ['/usr/bin/nm', '-S', '-C', '--defined-only', str(image)],
            'full.disassembly': ['/usr/bin/objdump', '-d', '-w', '-C', '-Mintel', '--no-show-raw-insn', str(image)],
            'sections.txt': ['/usr/bin/readelf', '-SW', str(image)],
            'rodata.txt': ['/usr/bin/objdump', '-s', '-j', '.rodata', str(image)],
        }
        for name, command in commands.items():
            with (directory / name).open('xb') as stdout, (directory / (name + '.stderr')).open('xb') as stderr:
                p = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=60)
            assert p.returncode == 0 and (directory / (name + '.stderr')).stat().st_size == 0
        symbols = []
        for line in (directory / 'nm.txt').read_text().splitlines():
            match = re.fullmatch(r'([0-9a-f]+) ([0-9a-f]+) ([A-Za-z]) (.+)', line)
            if match:
                symbols.append({'address': int(match[1], 16), 'size': int(match[2], 16),
                                'type': match[3], 'name': match[4]})
        activity = [x for x in symbols if any(prefix in x['name'] for prefix in ('rook2::movegen::', 'rook2::ordinary::', 'rook2::quiescence::', 'rook2::engine::'))]
        assembly = (directory / 'full.disassembly').read_text()
        starts = list(re.finditer(r'^([0-9a-f]+) <(.+)>:\n', assembly, re.M))
        blocks = {int(m[1], 16): assembly[m.start():starts[i + 1].start() if i + 1 < len(starts) else None]
                  for i, m in enumerate(starts)}
        for symbol in activity:
            if symbol['type'] in ('t', 'T'):
                body = blocks[symbol['address']]
                file = directory / ('generation-caller-' + hex(symbol['address'])[2:] + '.asm')
                file.write_text(body)
                symbol['capture'] = str(file)
        assert sha(image) == expected
        result['images'][label] = {'image': str(image), 'sha256': expected, 'bytes': image.stat().st_size,
                                   'commands': commands, 'generation_caller_symbols': activity,
                                   'text_bytes': sum(x['size'] for x in symbols if x['type'] in ('t', 'T')),
                                   'captured_files_sha256': {p.name: sha(p) for p in directory.iterdir()}}
    (out / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'engines_run': 0, 'generation_caller_symbols': {
        label: image['generation_caller_symbols'] for label, image in result['images'].items()}}))


if __name__ == '__main__':
    main()
