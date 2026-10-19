"""64 independent Boolean lanes. No per-lane loop or scalar classifier here."""
M = (1 << 64) - 1
TIERS = (1, 3, 5, 9, 99)


def add_bits(a, b, width=4):
    carry = 0
    result = []
    for i in range(width):
        x = a[i] if i < len(a) else 0
        y = b[i] if i < len(b) else 0
        result.append(x ^ y ^ carry)
        carry = (x & y) | ((x ^ y) & carry)
    return tuple(result)


def profile_features(x):
    # Normalized counts: weak1bit, queen1bit, rook/minor/pawn2bits.
    total = add_bits((x[0],), (x[1],))
    for digit in ((x[2], x[3]), (x[4], x[5]), (x[6], x[7])):
        total = add_bits(total, digit)
    high = total[2] | total[3]  # raw sum is0..11; >=4 saturates to4.
    count = (total[0] & (M ^ high), total[1] & (M ^ high), high)
    present = {1: x[6] | x[7], 3: x[4] | x[5],
               5: x[2] | x[3], 9: x[1], 99: x[0]}
    seen = 0
    least = {}
    for value in TIERS:
        least[value] = present[value] & (M ^ seen)
        seen |= present[value]
    return {"count": count, "least": least, "nonzero": seen}


def saturating_subtract(x, amount):
    # Subtract a single mixed-radix contribution after normalization.
    shift = {2: 1, 4: 2, 16: 4}[amount]
    result = list(x[:shift])
    borrow = M
    for i in range(shift, 8):
        result.append(x[i] ^ borrow)
        borrow &= M ^ x[i]
    keep = M ^ borrow
    return tuple(bit & keep for bit in result)


def unsigned_leq(a, b):
    equal = M
    less = 0
    for i in range(len(a) - 1, -1, -1):
        less |= equal & (M ^ a[i]) & b[i]
        equal &= M ^ (a[i] ^ b[i])
    return less | equal


def relation_from_features(own, opponent, tested):
    assert tested in (1, 3, 5, 9)
    a_le_d = unsigned_leq(opponent["count"], own["count"])
    greater = 0
    for v in TIERS:
        if v > tested:
            greater |= opponent["least"][v]
    greater_sum = 0
    for u in TIERS:
        allowed = 0
        for v in TIERS:
            if v > tested + u:
                allowed |= opponent["least"][v]
        greater_sum |= own["least"][u] & allowed
    favorable = (M ^ opponent["nonzero"]) | (
        own["nonzero"] & greater & (a_le_d | greater_sum))
    contested = opponent["nonzero"] & own["nonzero"] & (
        opponent["least"].get(tested, 0)) & a_le_d
    assert not favorable & contested
    # Two category-bit planes:0=unfavorable,1=contested,2=favorable.
    return contested, favorable


def victim_masks(x):
    nonempty = 0
    for bit in x:
        nonempty |= bit
    kinds = {}
    for tag in range(1, 7):
        mask = nonempty
        for i in range(3):
            mask &= x[i] if tag & (1 << i) else M ^ x[i]
        kinds[tag] = mask
    valid = M ^ nonempty
    for mask in kinds.values():
        valid |= mask
    if valid != M:
        raise ValueError("nonempty invalid Piece kind code")
    return {"empty": M ^ nonempty, "kind": kinds,
            "white": nonempty & (M ^ x[3]), "black": nonempty & x[3]}


def capture_priority(category, victim, kind):
    assert kind in ("N", "B", "R", "Q")
    two = three = 0
    if kind in ("N", "B"):
        two = victim["kind"][2] | victim["kind"][3]
        three = victim["kind"][4] | victim["kind"][5] | victim["kind"][6]
    elif kind == "R":
        two = victim["kind"][4]
        three = victim["kind"][5] | victim["kind"][6]
    keep = M ^ (two | three)
    return (category[0] & keep) | three, (category[1] & keep) | two | three


def direct_category(adjusted, opponent_zero, victim, kind):
    if kind == "Q":
        shortcut = opponent_zero | victim["kind"][5]
    elif kind == "N":
        shortcut = opponent_zero
    else:
        shortcut = opponent_zero & victim["empty"]
    keep = M ^ shortcut
    return capture_priority((adjusted[0] & keep,
                             (adjusted[1] & keep) | shortcut), victim, kind)


def occupancy_admission(victim, side):
    assert side in (0, 1)
    return victim["empty"] | victim["black" if side == 0 else "white"]
