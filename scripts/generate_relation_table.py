#!/usr/bin/env python3
"""Regenerate the immutable relation tables from the general numeric formula.

This is an offline maintenance helper, not a build/runtime dependency. It never
reads fixtures or expected answers. Deterministic formatting reproduces the
frozen typed full-byte-pair source without invoking Rust tools.
"""
import argparse
from pathlib import Path
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
    # Each row is own-major, opponent-minor: (own << 8) | opponent.
    profiles = [features(code) for code in range(256)]
    symbols = {'Unfavorable': 'U', 'Contested': 'C', 'Favorable': 'F'}
    lines = [
        '//! Generated from the general EVAL-RELATIONS formula; no fixture input.',
        '//! Rows: pawn, minor, rook, queen; index: (own << 8) | opponent.',
        'use crate::influence::Relation;',
        'use crate::influence::Relation::{Contested as C, Favorable as F, Unfavorable as U};',
        '',
        'pub(crate) static RELATIONS: [[Relation; 65_536]; 4] = [',
    ]
    for tested in [1, 3, 5, 9]:
        lines.append('    [')
        for own in profiles:
            row = [symbols[relation(own, opponent, tested)] for opponent in profiles]
            for start in range(0, 256, 64):
                lines.append('        ' + ', '.join(row[start:start + 64]) + ',')
        lines.append('    ],')
    lines.append('];')
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', type=Path, help='Verify exact existing source bytes without writing it')
    mode.add_argument('--output', type=Path, help='Write generated source bytes to this path')
    args = parser.parse_args()
    generated = generate()
    if args.check:
        if args.check.read_bytes() != generated.encode():
            parser.exit(1, 'generated relation source differs\n')
        print('Exact relation table source matches the general formula generator')
    elif args.output:
        args.output.write_bytes(generated.encode())
    else:
        sys.stdout.write(generated)


if __name__ == '__main__':
    main()
