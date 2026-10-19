"""Standalone algebra model only; imports no engine, runner, fixtures or profile."""
import json
from pathlib import Path
from random import Random
MASK = (1 << 64) - 1

def encode(values):
    return [sum(((v >> b) & 1) << j for j, v in enumerate(values)) for b in range(8)]

def decode_reference(planes):
    return [sum(((planes[b] >> j) & 1) << b for b in range(8)) for j in range(64)]

def add_mask(planes, mask, shift):
    # Ripple carry independently at each target. Carry beyond bit7 is discarded.
    for b in range(shift, 8):
        old = planes[b]
        planes[b] = old ^ mask
        mask &= old

def add_source(planes, normal, weak, shift):
    assert normal & weak == 0 and 1 <= shift <= 6
    if not weak:
        add_mask(planes, normal, shift)
        return
    # Lower weak carry remains a subset of original weak, disjoint from normal.
    carry = weak
    for b in range(shift):
        old = planes[b]
        planes[b] = old ^ carry
        carry &= old
    add_mask(planes, carry | normal, shift)

def transpose_butterfly(planes):
    a = list(planes)
    for shift, mask in [(4, 0x0f0f0f0f0f0f0f0f),
                        (2, 0x3333333333333333),
                        (1, 0x5555555555555555)]:
        for i in range(8):
            if i & shift:
                continue
            j = i | shift
            t = ((a[i] >> shift) ^ a[j]) & mask
            a[j] ^= t
            a[i] ^= t << shift
    # Word a[j] now holds target bytes j,j+8,...,j+56.
    # Model the exact baseline SSE2 final byte-transpose network, not a LUT.
    v = [list(x.to_bytes(8, 'little')) + [0]*8 for x in a]
    def unpack(x, y, width, high=False):
        start = 8 if high else 0
        out = []
        for k in range(start, start+8, width):
            out += x[k:k+width] + y[k:k+width]
        return out
    u = [unpack(v[i], v[i+1], 1) for i in range(0, 8, 2)]
    w = [unpack(u[0], u[1], 2), unpack(u[0], u[1], 2, True),
         unpack(u[2], u[3], 2), unpack(u[2], u[3], 2, True)]
    z = [unpack(w[0], w[2], 4), unpack(w[0], w[2], 4, True),
         unpack(w[1], w[3], 4), unpack(w[1], w[3], 4, True)]
    return sum(z, [])

def coordinates(square, offsets):
    f, r = square % 8, square // 8
    return sum(1 << (8*(r+dr)+f+df) for df,dr in offsets
               if 0 <= f+df < 8 and 0 <= r+dr < 8)

DIRS = [(-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(1,0),(0,-1),(0,1)]
KNIGHTS = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]

def coordinate_masks(board, side, source, kind):
    # Semantic witnesses only: unchanged native slider_masks remains owner.
    normal = weak = 0
    for df,dr in DIRS:
        diag = df != 0 and dr != 0
        if (kind == 'B' and not diag) or (kind == 'R' and diag):
            continue
        f,r = source % 8, source // 8
        weakened = False
        while 0 <= f+df < 8 and 0 <= r+dr < 8:
            f += df; r += dr; target = 8*r+f
            if weakened: weak |= 1 << target
            else: normal |= 1 << target
            piece = board.get(target)
            if piece is None: continue
            color, occupant = piece
            if color == side and occupant == 'Q':
                weakened = True; continue
            if color != side and occupant == 'K': continue
            if color == side and occupant == ('B' if diag else 'R'): continue
            if color == side and occupant == 'P' and diag and dr == (1 if side == 0 else -1):
                if 0 <= f+df < 8 and 0 <= r+dr < 8:
                    extra = 8*(r+dr)+f+df
                    if weakened: weak |= 1 << extra
                    else: normal |= 1 << extra
            break
    assert normal & weak == 0
    return normal,weak

def run():
    rng = Random(0x38b17)
    cases = {'transpose_basis':0,'transpose_random':0,'all_byte_additions':0,
             'sequential_sources':0,'geometry_mask_equivalence':0,'board_witnesses':0}
    for b in range(8):
        for j in range(64):
            p = [0]*8; p[b] = 1 << j
            assert transpose_butterfly(p) == decode_reference(p)
            cases['transpose_basis'] += 1
    for _ in range(256):
        p = [rng.getrandbits(64) for _ in range(8)]
        assert transpose_butterfly(p) == decode_reference(p)
        cases['transpose_random'] += 1
    for prior in range(256):
        for shift in range(7):
            p = encode([prior]*64)
            add_mask(p, MASK, shift)
            assert transpose_butterfly(p) == [(prior + (1 << shift)) & 255]*64
            cases['all_byte_additions'] += 1
    for _ in range(128):
        scalar = [rng.randrange(256) for _ in range(64)]
        p = encode(scalar)
        for step in range(48):
            normal = rng.getrandbits(64)
            weak = rng.getrandbits(64) & ~normal & MASK
            shift = rng.choice([1,2,4])
            add_source(p,normal,weak,shift)
            scalar = [(v + (((normal>>j)&1)<<shift) + ((weak>>j)&1)) & 255
                      for j,v in enumerate(scalar)]
            assert transpose_butterfly(p) == scalar
            cases['sequential_sources'] += 1
    # Existing mask storage: source lookup for pawn targets uses opposite color.
    for square in range(64):
        assert coordinates(square,KNIGHTS) == coordinates(square,[(-x,-y) for x,y in KNIGHTS])
        assert coordinates(square,DIRS) == coordinates(square,[(-x,-y) for x,y in DIRS])
        for side in [0,1]:
            forward = 1 if side == 0 else -1
            back_of_opponent = -1 if (1-side) == 0 else 1
            assert coordinates(square,[(-1,forward),(1,forward)]) == coordinates(square,[(-1,back_of_opponent),(1,back_of_opponent)])
            cases['geometry_mask_equivalence'] += 1
    # Multiple promoted sliders, own-queen weakening, enemy king transparency.
    sq = lambda s: ord(s[0])-97 + 8*(int(s[1])-1)
    board = {sq(s):(c,k) for s,c,k in [('a1',0,'K'),('h8',1,'K'),
        ('a4',0,'Q'),('c4',0,'Q'),('e4',0,'Q'),('g4',1,'K'),
        ('b2',0,'B'),('d6',0,'B'),('a8',1,'R'),('h6',1,'R'),
        ('e5',1,'Q'),('f3',1,'Q'),('d3',0,'P'),('g5',1,'P')]}
    # Avoid two black kings; retain g4 to make beyond-king transparency observable.
    del board[sq('h8')]
    normal,weak = coordinate_masks(board,0,sq('a4'),'Q')
    assert normal & (1 << sq('c4'))
    assert weak & (1 << sq('h4'))  # through own queens and opposing king.
    for reflected in [False,True]:
        b = {(s^56 if reflected else s):((1-c if reflected else c),k)
             for s,(c,k) in board.items()}
        for side in [0,1]:
            p = [0]*8; scalar = [0]*64
            for source,(color,kind) in b.items():
                if color != side: continue
                if kind in 'BRQ':
                    n,w = coordinate_masks(b,side,source,kind)
                    shift = {'B':4,'R':2,'Q':1}[kind]
                    add_source(p,n,w,shift)
                else:
                    shift = {'P':6,'N':4,'K':0}[kind]
                    offsets = DIRS if kind == 'K' else KNIGHTS if kind == 'N' else [(-1,1 if side==0 else -1),(1,1 if side==0 else -1)]
                    n,w = coordinates(source,offsets),0
                    add_mask(p,n,shift)
                for target in range(64):
                    scalar[target] = (scalar[target]+(((n>>target)&1)<<shift)+((w>>target)&1)) & 255
            assert transpose_butterfly(p) == scalar
            cases['board_witnesses'] += 1
    # Explicit complete-byte overflow: 8 minors + 2 pawns = 256 -> 0.
    p = [0]*8
    for _ in range(8): add_mask(p,1<<27,4)
    for _ in range(2): add_mask(p,1<<27,6)
    assert transpose_butterfly(p)[27] == 0
    result = {'complete':True,'scope':'pure Python algebra, not native producer or runtime validation',
              'cases':cases,'explicit_mod256_carry_witness':True,
              'transpose_word_pairs':12,'transpose_pair_boolean_shift_ops':72,
              'transpose_sse2_unpack_ops':12,'failures':[]}
    Path(__file__).with_name('model-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__ == '__main__': run()
