#!/usr/bin/env python3
"""Regenerate the immutable relation tables from the general numeric formula.

This is an offline maintenance helper, not a build/runtime dependency. It never
reads fixtures or expected answers. rustfmt normalizes the emitted Rust source.
"""
import argparse
from pathlib import Path
import subprocess
import sys


def features(code):
    digits = [code % 2, code // 2 % 2, code // 4 % 4, code // 16 % 4, code // 64 % 4]
    count = min(sum(digits), 4)
    tier = next((tier for value, tier in zip(reversed(digits), [1, 3, 5, 9, 99]) if value), 0)
    return count, tier


def relation(own, opponent, tested):
    defenses, own_tier = own
    attacks, attack_tier = opponent
    if attacks == 0:
        return 'Favorable'
    if defenses == 0 or attack_tier < tested:
        return 'Unfavorable'
    if attack_tier == tested:
        return 'Contested' if attacks <= defenses else 'Unfavorable'
    return 'Favorable' if attacks <= defenses or attack_tier > tested + own_tier else 'Unfavorable'


def generate():
    states = sorted({features(code) for code in range(256)})
    assert len(states) == 16
    classes = [states.index(features(code)) for code in range(256)]
    lines = ['//! Generated from EVAL-RELATIONS features/formula; no fixture input.',
             'use crate::influence::Relation;', 'pub(crate) static CLASS: [u8;256] = [']
    lines.extend('    ' + ','.join(map(str, classes[i:i + 16])) + ',' for i in range(0, 256, 16))
    lines.extend(['];', 'pub(crate) static RELATIONS: [[Relation;256];4] = ['])
    for tested in [1, 3, 5, 9]:
        lines.append('    [')
        lines.extend('        ' + ','.join('Relation::' + relation(own, opponent, tested) for opponent in states) + ',' for own in states)
        lines.append('    ],')
    lines.append('];\n')
    formatted = subprocess.run(['rustfmt', '--config', 'skip_children=true'],
                               input='\n'.join(lines), capture_output=True, text=True, check=True)
    return formatted.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', type=Path, help='Verify exact existing source bytes without writing it')
    args = parser.parse_args()
    generated = generate()
    if args.check:
        if args.check.read_bytes() != generated.encode():
            parser.exit(1, 'generated relation source differs\n')
        print('Exact relation table source matches the general formula generator')
    else:
        sys.stdout.write(generated)


if __name__ == '__main__':
    main()
