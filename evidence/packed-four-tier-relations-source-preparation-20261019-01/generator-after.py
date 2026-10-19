#!/usr/bin/env python3
"""Regenerate the immutable packed four-tier relation table from the general numeric formula.

This is an offline maintenance helper, not a build/runtime dependency. It never
reads fixtures or expected answers. Deterministic formatting reproduces the
packed own-major full-byte-pair source without invoking Rust tools.
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
        return 2
    if defenses == 0 or attack_tier < tested:
        return 0
    if attack_tier == tested:
        return 1 if attacks <= defenses else 0
    return 2 if attacks <= defenses or attack_tier > tested + own_tier else 0


def generate_payload():
    # Index remains own-major, opponent-minor. Low to high 2-bit fields are
    # pawn, N/B, rook, queen; each general formula result is exactly 0,1 or2.
    profiles = [features(code) for code in range(256)]
    return bytes(sum(relation(own, opponent, tested) << (2 * field)
                     for field, tested in enumerate([1, 3, 5, 9]))
                 for own in profiles for opponent in profiles)


def generate():
    payload = generate_payload()
    lines = [
        '//! Generated from the general EVAL-RELATIONS formula; no fixture input.',
        '//! Index: (own << 8) | opponent; 2-bit fields low-to-high: P, N/B, R, Q.',
        '//! Every field is 0=Unfavorable, 1=Contested or 2=Favorable.',
        '',
        'pub(crate) static RELATIONS: [u8; 65_536] = [',
    ]
    for start in range(0, len(payload), 32):
        lines.append('    ' + ', '.join(f'0x{value:02x}' for value in payload[start:start + 32]) + ',')
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
