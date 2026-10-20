#!/usr/bin/env python3
"""Emit typed byte-pair relations from general EVAL-RELATIONS; no input corpus."""
import argparse
from pathlib import Path


def features(code):
    # Decode all five normalized mixed-radix digits in weak-to-pawn order.
    weak = code % 2
    queen = (code // 2) % 2
    rook = (code // 4) % 4
    minor = (code // 16) % 4
    pawn = (code // 64) % 4
    count = min(weak + queen + rook + minor + pawn, 4)
    tier = next((value for present, value in
                 [(pawn, 1), (minor, 3), (rook, 5), (queen, 9), (weak, 99)]
                 if present), 0)
    return count, tier


def outcome(own, opponent, tested):
    d, u = own
    a, v = opponent
    if a == 0:
        return 'F'
    if d == 0 or v < tested:
        return 'U'
    if v == tested:
        return 'C' if a <= d else 'U'
    return 'F' if a <= d or v > tested + u else 'U'


def source():
    # Each row is own-major, opponent-minor: (own << 8) | opponent.
    profiles = [features(code) for code in range(256)]
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
            row = [outcome(own, opponent, tested) for opponent in profiles]
            for start in range(0, 256, 64):
                lines.append('        ' + ', '.join(row[start:start + 64]) + ',')
        lines.append('    ],')
    lines.append('];')
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with args.output.open('x') as stream:
        stream.write(source())


if __name__ == '__main__':
    main()
