"""Finite offline proof controls; scalar transpose/reference remain test-only."""
from pathlib import Path
import hashlib
import json
import sys
import model
P = Path(__file__).resolve().parent
RADICES = (2, 2, 4, 4, 4)
TIERS = (99, 9, 5, 3, 1)


def digits(byte):
    out = []
    for radix in RADICES:
        byte, digit = divmod(byte, radix)
        out.append(digit)
    assert byte == 0
    return tuple(out)


def exclude(counts, amount):
    # Category borrowing over explicit independent radix digits, not byte minus.
    category = {2: 1, 4: 2, 16: 3}[amount]
    out = list(counts)
    for at in range(category, 5):
        if out[at]:
            out[at] -= 1
            for lower in range(category, at):
                out[lower] = RADICES[lower] - 1
            return tuple(out)
    return (0, 0, 0, 0, 0)


def scalar_relation(own, opponent, tested):
    d = min(sum(own), 4)
    a = min(sum(opponent), 4)
    if a == 0:
        return 2
    u = min((v for v, n in zip(TIERS, own) if n), default=0)
    v = min(value for value, n in zip(TIERS, opponent) if n)
    if d == 0 or v < tested:
        return 0
    if v == tested:
        return 1 if a <= d else 0
    return 2 if a <= d or v > tested + u else 0


def transpose(values):
    assert len(values) == 64 and all(0 <= v <= 255 for v in values)
    return tuple(sum(((v >> bit) & 1) << lane for lane, v in enumerate(values))
                 for bit in range(8))


def unpack(planes):
    return [sum(((bit >> lane) & 1) << i for i, bit in enumerate(planes))
            for lane in range(64)]


def reference_priority(kind, byte, category):
    if byte == 0:
        return category
    tag = byte % 8
    if not 1 <= tag <= 6:
        raise ValueError("invalid native kind")
    if kind in ("N", "B"):
        return {2: 2, 3: 2, 4: 3, 5: 3, 6: 3}.get(tag, category)
    if kind == "R":
        return {4: 2, 5: 3, 6: 3}.get(tag, category)
    return category


def reference_direct(kind, byte, adjusted, opponent_zero):
    shortcut = ((opponent_zero or (byte != 0 and byte % 8 == 5)) if kind == "Q"
                else opponent_zero and (kind == "N" or byte == 0))
    return reference_priority(kind, byte, 2 if shortcut else adjusted)


def check_equal(got, want, context):
    if got != want:
        raise AssertionError({"context": context, "got": got, "want": want})


def verify():
    pinpaths = [P / "model.py", P / "verify.py",
        Path('/home/legolas/king-spec/spec/evaluation-relations.md'),
        Path('/home/legolas/king-spec/spec/activity.md'),
        Path('/home/legolas/rook2/src/influence.rs'),
        Path('/home/legolas/rook2/src/activity.rs'),
        Path('/home/legolas/rook2/src/types.rs')]
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    pins = {str(p): sha(p) for p in pinpaths}
    explicit = [digits(x) for x in range(256)]
    excluded = {a: [exclude(d, a) for d in explicit] for a in (2, 4, 16)}
    feature_checks = borrow_checks = relation_checks = 0
    direct_fullpair_checks = 0
    outcomes = set()
    for start in range(0, 256, 64):
        values = list(range(start, start + 64))
        bits = transpose(values)
        f = model.profile_features(bits)
        check_equal(unpack(f['count']), [min(sum(explicit[v]), 4) for v in values], 'capped count')
        for lane, v in enumerate(values):
            present = [t for t, m in f['least'].items() if (m >> lane) & 1]
            expected = [min((t for t, n in zip(TIERS, explicit[v]) if n), default=0)]
            check_equal(present or [0], expected, ['least tier', v])
            feature_checks += 1
        for amount in (2, 4, 16):
            check_equal(unpack(model.saturating_subtract(bits, amount)),
                [sum(d * w for d, w in zip(excluded[amount][v], (1, 2, 4, 16, 64))) for v in values],
                ['borrow', amount, start])
            borrow_checks += 64
    # Two bijections cover all65536 pairs; second makes own/opponent nonuniform
    # within each64-lane batch, guarding accidental lane mixing.
    for permutation in (False, True):
        for start in range(0, 65536, 64):
            ids = [((i * 257 + 31) % 65536 if permutation else i) for i in range(start, start + 64)]
            own = [i // 256 for i in ids]
            opp = [i % 256 for i in ids]
            ownbits, oppbits = transpose(own), transpose(opp)
            opf = model.profile_features(oppbits)
            derived = {}
            for amount in (0, 2, 4, 16):
                f = model.profile_features(ownbits if amount == 0 else model.saturating_subtract(ownbits, amount))
                for tested in (1, 3, 5, 9):
                    out = model.relation_from_features(f, opf, tested)
                    want = [scalar_relation(explicit[v] if amount == 0 else excluded[amount][v], explicit[o], tested)
                            for v, o in zip(own, opp)]
                    check_equal(unpack(out), want, ['relation', permutation, start, amount, tested])
                    derived[amount, tested] = (out, want)
                    relation_checks += 64
            # Integrated direct classification: each byte pair for all four
            # activity kinds with changing canonical victim codes across lanes.
            victims = [([0] + list(range(1, 7)) + list(range(9, 15)))[(i + start // 64) % 13] for i in range(64)]
            vm = model.victim_masks(transpose(victims))
            for kind, amount, tier in [('N', 16, 3), ('B', 16, 3), ('R', 4, 5), ('Q', 2, 9)]:
                bits, refs = derived[amount, tier]
                out = model.direct_category(bits, model.M ^ opf['nonzero'], vm, kind)
                want = [reference_direct(kind, v, c, o == 0) for v, c, o in zip(victims, refs, opp)]
                check_equal(unpack(out), want, ['direct integrated', permutation, start, kind])
                direct_fullpair_checks += 64
            n = model.direct_category(derived[16, 3][0], model.M ^ opf['nonzero'], vm, 'N')
            b = model.direct_category(derived[16, 3][0], model.M ^ opf['nonzero'], vm, 'B')
            check_equal(n, b, ['N/B actual full pairs', permutation, start])
    valid = [v for v in range(256) if v == 0 or 1 <= v % 8 <= 6]
    invalid = [v for v in range(256) if v not in valid]
    for byte in invalid:
        try:
            model.victim_masks(transpose([byte] * 64))
        except ValueError:
            pass
        else:
            raise AssertionError(['invalid victim accepted', byte])
    capture_checks = direct_factored_checks = admission_checks = equality_checks = 0
    # Exhaustive finite override product: all193 valid raw Piece bytes (including
    # aliases of canonical tags), both mover colors, all0..3 base categories,
    # and both opponent-zero statuses. This factor is independent of byte pair.
    cases = [(v, side, base, zero) for v in valid for side in (0, 1)
             for base in range(4) for zero in (False, True)]
    for start in range(0, len(cases), 64):
        block = cases[start:start + 64]
        actual = len(block)
        block += [block[-1]] * (64 - len(block))
        victims = [x[0] for x in block]
        bases = [x[2] for x in block]
        zero = sum(int(x[3]) << lane for lane, x in enumerate(block))
        vm = model.victim_masks(transpose(victims))
        cat = transpose(bases)[:2]
        for kind in ('N', 'B', 'R', 'Q'):
            p = unpack(model.capture_priority(cat, vm, kind))
            d = unpack(model.direct_category(cat, zero, vm, kind))
            for lane, (victim, side, base, opzero) in enumerate(block[:actual]):
                check_equal(p[lane], reference_priority(kind, victim, base), ['priority', kind, block[lane]])
                check_equal(d[lane], reference_direct(kind, victim, base, opzero), ['direct factor', kind, block[lane]])
                outcomes.add(d[lane]);capture_checks += 1;direct_factored_checks += 1
        n = unpack(model.direct_category(cat, zero, vm, 'N'))
        b = unpack(model.direct_category(cat, zero, vm, 'B'))
        for lane, (victim, side, base, opzero) in enumerate(block[:actual]):
            # Actual adjusted relation is always2 when opponent byte is0.
            if not opzero or base == 2:
                check_equal(n[lane], b[lane], ['N/B factor', block[lane]])
                equality_checks += 1
            admitted = model.occupancy_admission(vm, side)
            want = victim == 0 or ((victim // 8) % 2 != side)
            check_equal(bool((admitted >> lane) & 1), want, ['occupancy', block[lane]])
            admission_checks += 1
    check_equal(outcomes, {0, 1, 2, 3}, 'category range preserved')
    assert all(sha(Path(p)) == h for p, h in pins.items())
    result = {'complete': True, 'lanes': 64, 'byte_pairs_per_layout': 65536,
        'layouts': 2, 'tested_tiers': [1, 3, 5, 9], 'own_subtractions': [0, 2, 4, 16],
        'relation_lane_comparisons': relation_checks, 'profile_feature_lanes': feature_checks,
        'borrow_lane_comparisons': borrow_checks, 'integrated_direct_lane_comparisons': direct_fullpair_checks,
        'valid_victim_bytes': len(valid), 'rejected_invalid_victim_bytes': len(invalid),
        'capture_priority_comparisons': capture_checks, 'direct_override_comparisons': direct_factored_checks,
        'occupancy_admission_comparisons': admission_checks, 'minor_direct_equality_comparisons': equality_checks,
        'categories_observed': sorted(outcomes), 'all_inputs_unchanged': True,
        'candidate_kernel_per_lane_scalar_classifier': False,
        'geometry_or_mobility_integration': False, 'performance_claim': False, 'input_pins': pins}
    (P / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'input_pins'}, indent=2))


if __name__ == '__main__':
    try:
        verify()
    except BaseException as error:
        failure = {'complete': False, 'error_type': type(error).__name__, 'error': str(error),
                   'model_sha256': hashlib.sha256((P / 'model.py').read_bytes()).hexdigest(),
                   'verify_sha256': hashlib.sha256((P / 'verify.py').read_bytes()).hexdigest()}
        with (P / 'failure.json').open('x') as file:
            json.dump(failure, file, indent=2);file.write('\n')
        raise
