#!/usr/bin/python3
"""Finite pure geometry identities only; no Rust/native engine is executed."""
import hashlib
import itertools
import json
from pathlib import Path
MASK = (1 << 64) - 1

def nearest(bits, increasing):
    return bits & -bits if increasing else (1 << (bits.bit_length() - 1) if bits else 0)

def prefix(ray, blocker, increasing):
    if not blocker:
        return ray
    return ray & (blocker | ((blocker - 1) & MASK)) if increasing else ray & (~((blocker - 1) & MASK) & MASK)

def selected(bits, increasing):
    out = []
    while bits:
        first = nearest(bits, increasing)
        out.append(first.bit_length() - 1)
        bits ^= first
    return out

def prove():
    checks = 0
    for length in range(8):
        # States: empty, transparent friendly/enemy, opaque friendly/enemy.
        for states in itertools.product(range(5), repeat=length):
            for stride in (1, 9):
                for increasing in (False, True):
                    squares = [i * stride if increasing else 63 - i * stride for i in range(length)]
                    ray = sum(1 << i for i in squares)
                    occupied = sum(1 << i for i, state in zip(squares, states) if state)
                    friendly = sum(1 << i for i, state in zip(squares, states) if state in (1, 3))
                    opaque = sum(1 << i for i, state in zip(squares, states) if state in (3, 4))
                    direct = prefix(ray, nearest(ray & occupied, increasing), increasing)
                    visited = prefix(ray, nearest(ray & opaque, increasing), increasing)
                    actual = [(i, False) for i in selected(direct & ~friendly, increasing)]
                    actual += [(i, True) for i in selected((visited & ~direct) & ~friendly, increasing)]
                    expected = []
                    extra = False
                    for square, state in zip(squares, states):
                        if state not in (1, 3):
                            expected.append((square, extra))
                        if state in (3, 4):
                            break
                        if state:
                            extra = True
                    assert actual == expected, (states, squares, actual, expected)
                    checks += 1
    tags = 0
    # Canonical nonempty tags only: 1..6 (white), 9..14 (black).
    # This proves decoding vs logical activity transparency, not generic public aliases.
    for code in (0, *range(1, 7), *range(9, 15)):
        p0, p1, p2, black = ((code >> bit) & 1 for bit in range(4))
        occupied = p0 | p1 | p2
        decoded = {'pawn': p0 & (1-p1) & (1-p2), 'knight': (1-p0) & p1 & (1-p2),
            'bishop': p0 & p1 & (1-p2), 'rook': (1-p0) & (1-p1) & p2,
            'queen': p0 & (1-p1) & p2}
        for color in (0, 1):
            friendly = occupied & (black if color else 1-black)
            enemy = occupied & (1-friendly)
            for kind in ('bishop', 'rook', 'queen'):
                for direction in range(8):
                    transparent = enemy | (friendly & (decoded['knight'] | decoded['rook'])) if kind == 'bishop' else ((enemy & (1-decoded['pawn'])) | (friendly & decoded['rook']) if kind == 'rook' else 0)
                    if kind == 'rook' and direction == (4 if color == 0 else 5):
                        transparent |= friendly & (decoded['knight'] | decoded['bishop'] | decoded['queen'])
                    victim_kind = (code & 7) - 1
                    own = bool(occupied and black == color)
                    expected = False
                    if occupied and kind == 'bishop':
                        expected = not own or victim_kind in (1, 3)
                    elif occupied and kind == 'rook':
                        expected = (not own and victim_kind != 0) or (own and (victim_kind == 3 or (direction == (4 if color == 0 else 5) and victim_kind in (1, 2, 4))))
                    assert bool(transparent) == expected, (code, color, kind, direction)
                    tags += 1
    return {'pure_prefix_ordered_cases': checks, 'canonical_tag_transparency_cases': tags,
        'bit_edges': [0, 63], 'ray_lengths': list(range(8)), 'ray_strides': [1, 9],
        'zero_blocker_and_empty_ray_included': True, 'ordered_direct_then_additional_equal': True,
        'all_assertions_passed': True,
        'limitations': ['No Rust parse/build/native tests.', 'No activity numerical differential execution.',
            'Canonical coherent tags only for transparency decoding; public arbitrary placement remains scalar.',
            'Fixed unmodified ray-table correspondence is a source obligation, not generated here.']}

if __name__ == '__main__':
    result = prove()
    result['helper_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    out = Path(__file__).with_name('offline-prefix-proof.json')
    assert not out.exists()
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))
