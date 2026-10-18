//! Specified geometric endgame reductions and final score/bound composition.
use crate::position::Position;
use crate::types::{Color, PieceKind, Square};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Point {
    f: i32,
    r: i32,
}
impl Point {
    fn new(f: i32, r: i32) -> Self {
        Self { f, r }
    }
    fn of(square: Square, side: Color, flip: bool) -> Self {
        let f = square.file() as i32 + 1;
        let r = square.rank() as i32 + 1;
        Self {
            f: if flip { 9 - f } else { f },
            r: if side == Color::White { r } else { 9 - r },
        }
    }
    fn offset(self, f: i32, r: i32) -> Self {
        Self::new(self.f + f, self.r + r)
    }
    fn distance(self, other: Self) -> i32 {
        (self.f - other.f).abs().max((self.r - other.r).abs())
    }
    fn adjacent(self, other: Self) -> bool {
        self.distance(other) == 1
    }
    fn aligned(self, other: Self) -> bool {
        self.f == other.f
            || self.r == other.r
            || (self.f - other.f).abs() == (self.r - other.r).abs()
    }
}

pub fn pawn_race(side: Color, king: Square, pawn: Square, other: Square, turn: Color) -> i32 {
    let flip = pawn.file() >= 4;
    let p = Point::of(pawn, side, flip);
    let a = Point::of(king, side, flip);
    let k = Point::of(other, side, flip);
    let t = i32::from(turn == side);
    if matches!(
        (t, p.f, p.r, a.f, a.r, k.f, k.r),
        (0, 2, 6, 3, 6, 1, 7)
            | (0, 2, 6, 3, 7, 1, 8)
            | (0, 1, 7, 1, 8, 4, 6..=8)
            | (0, 2, 6, 3, 8, 1, 8)
            | (1, 2, 6, 3, 6, 1, 8)
            | (1, 1, 7, 1, 8, 3, 7..=8)
    ) {
        return -1;
    }
    if t == 0 && k.adjacent(p) && !a.adjacent(p) {
        return -1;
    }
    if 9 - p.r - t - i32::from(p.r == 2) < k.distance(Point::new(p.f, 8)) {
        return 1;
    }
    if (p.r + t..=8).all(|r| a.adjacent(Point::new(p.f, r))) {
        return 1;
    }
    if p.r == 2 {
        if k.distance(p) < a.distance(p) - t - 1 && k.r >= 3 {
            return -1;
        }
    } else if k.distance(p) + i32::from((k.f - p.f).abs() == (k.r - p.r).abs()) < a.distance(p) - t
    {
        return -1;
    }
    if p.f == 1 {
        if a.r == 6
            && (1..=3).contains(&a.f)
            && k.f == 3
            && (k.r == 7 || k.r == 8)
            && p.r == if t == 1 { 6 } else { 7 }
        {
            return 1;
        }
        if k.distance(Point::new(3, 8))
            <= a.distance(Point::new(2, 7))
                .min(a.distance(Point::new(2, 8)))
                - t
        {
            return -1;
        }
        if k.f <= 2 && k.r > p.r {
            return -1;
        }
        if a.f == 1 && k.f <= 4 - t && k.r > t + 2 && k.r >= p.r + t {
            return -1;
        }
        return 0;
    }
    if p.r == 7 {
        return 0;
    }
    if a.f == p.f && a.r == 6 && k.r >= 6 {
        return 1;
    }
    if (a.f - p.f).abs() <= 1 && a.r == p.r + 2 {
        return 1;
    }
    if p.r >= 5 && (a.f - p.f).abs() <= 1 && a.r == p.r + 1 {
        return 1;
    }
    if k == p.offset(0, 1) {
        return -1;
    }
    let opposition = |n| {
        if t == 1 {
            k == a.offset(0, n)
        } else {
            k.adjacent(a.offset(0, n))
        }
    };
    if a.adjacent(p) && opposition(2) {
        return -1;
    }
    if p.r == 6 {
        return i32::from(a.r == p.r && (a.f - p.f).abs() == 1);
    }
    if k == p.offset(0, 2)
        || ((k == p.offset(-1, 2) || k == p.offset(1, 2)) && a.r < p.r)
        || (p.r <= 4 && a.r == p.r + 1 && opposition(2))
        || (a.r == p.r && opposition(4))
    {
        -1
    } else {
        0
    }
}

fn nonpawns(c: &[u8; 6]) -> u16 {
    c[1..5].iter().map(|&n| n as u16).sum()
}
fn total(c: &[u8; 6]) -> u16 {
    c[0] as u16 + nonpawns(c)
}
fn material(c: &[u8; 6]) -> (u8, u8, u8, u8) {
    (c[1], c[2], c[3], c[4])
}
fn king(position: &Position, side: Color) -> Square {
    position.piece_squares(side, PieceKind::King)[0]
}
fn one(position: &Position, side: Color, kind: PieceKind) -> Square {
    position.piece_squares(side, kind)[0]
}
fn sign(side: Color) -> i32 {
    if side == Color::White {
        1
    } else {
        -1
    }
}

pub fn pawnless_potential(score: i32, own: &[u8; 6], other: &[u8; 6]) -> i32 {
    let opponent = nonpawns(other);
    match material(own) {
        (0, 0, 0, 0) | (1, 0, 0, 0) | (0, 1, 0, 0) => 0,
        (2, 0, 0, 0) => {
            if total(other) == 0 {
                0
            } else if opponent == 0 {
                score / 2
            } else {
                score / 4
            }
        }
        (0, 2, 0, 0) | (1, 1, 0, 0) | (0, 0, 1, 0) if opponent != 0 => score / 4,
        (1, 0, 1, 0) | (0, 1, 1, 0) if other[3] != 0 || other[4] != 0 => (3 * score) / 16,
        (1, 0, 0, 1) | (0, 1, 0, 1) if other[4] != 0 => score / 2,
        _ => score,
    }
}

pub fn minor_mate(stronger: Square, weaker: Square, bishop: Square) -> i32 {
    let a = Point::of(stronger, Color::White, false);
    let k = Point::of(weaker, Color::White, false);
    let b = Point::of(bishop, Color::White, false);
    let corners = if (b.f + b.r) % 2 == 0 {
        [Point::new(1, 1), Point::new(8, 8)]
    } else {
        [Point::new(1, 8), Point::new(8, 1)]
    };
    let rect = |x: Point, y: Point| (x.f - y.f).abs() + (x.r - y.r).abs();
    let d = rect(k, corners[0]).min(rect(k, corners[1]));
    15 * (55 - 2 * d - rect(a, k))
}

pub fn pawn_spread(position: &Position, score: i32, endgame: u16) -> i32 {
    let side = if score >= 0 {
        Color::White
    } else {
        Color::Black
    };
    let pawns = position.piece_squares(side, PieceKind::Pawn);
    adjust_span(score, endgame, pawns.iter().map(|s| s.file()))
}

pub fn pawn_spread_files(score: i32, endgame: u16, white: &[u8], black: &[u8]) -> i32 {
    adjust_span(
        score,
        endgame,
        if score >= 0 { white } else { black }.iter().copied(),
    )
}

fn adjust_span(score: i32, endgame: u16, files: impl Iterator<Item = u8>) -> i32 {
    let (low, high, any) = files.fold((7, 0, false), |(lo, hi, _), file| {
        (lo.min(file), hi.max(file), true)
    });
    let span = if any { high - low + 1 } else { 0 };
    let coefficient = match span {
        0..=3 => -10,
        4 => -6,
        5 => 0,
        _ => 3,
    };
    (score as i64 * (4096 + (endgame as i64 - 192) * coefficient) + 2048).div_euclid(4096) as i32
}

pub fn material_blend(position: &Position, score: i32, endgame: u16, progress: i32) -> i32 {
    let score = pawn_spread(position, score, endgame);
    let side = if score >= 0 {
        Color::White
    } else {
        Color::Black
    };
    let enemy = side.opponent();
    let own = &position.counts[side.index()];
    let other = &position.counts[enemy.index()];
    let mut adjusted = if own[0] == 0 {
        sign(side) * pawnless_potential(score.abs(), own, other)
    } else {
        score
    };
    if own[0] == 0 && material(own) == (1, 1, 0, 0) && total(other) == 0 {
        adjusted = sign(side)
            * minor_mate(
                king(position, side),
                king(position, enemy),
                one(position, side, PieceKind::Bishop),
            );
    } else if own[0] == 1
        && own[1] as u16 + own[2] as u16 == 1
        && own[3] == 0
        && own[4] == 0
        && nonpawns(other) != 0
    {
        if sign(side) * progress > 0 && progress.abs() < adjusted.abs() {
            adjusted = progress;
        }
        adjusted = adjusted.div_euclid(2);
    }
    let w = material(&position.counts[0]);
    let b = material(&position.counts[1]);
    let opposite_bishops = || {
        let w = one(position, Color::White, PieceKind::Bishop);
        let b = one(position, Color::Black, PieceKind::Bishop);
        (w.file() + w.rank()) % 2 != (b.file() + b.rank()) % 2
    };
    if w == (0, 0, 1, 0) && b == w || w == (0, 1, 1, 0) && b == w && opposite_bishops() {
        (3 * progress as i64 + 5 * adjusted as i64).div_euclid(8) as i32
    } else if w == (0, 1, 0, 0) && b == w && opposite_bishops() {
        (progress as i64 + adjusted as i64).div_euclid(2) as i32
    } else {
        adjusted
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Bounded {
    pub score: i32,
    pub lower: i32,
    pub upper: i32,
}

pub fn race_bounds(position: &Position, side: Color, mut value: Bounded) -> Bounded {
    let pawns = position.piece_squares(side, PieceKind::Pawn);
    if pawns.is_empty() {
        return value;
    }
    if pawns.len() > 1
        && !(pawns.iter().all(|s| s.file() == 0) || pawns.iter().all(|s| s.file() == 7))
    {
        return value;
    }
    let pawn = *pawns
        .iter()
        .max_by_key(|s| {
            if side == Color::White {
                s.rank()
            } else {
                7 - s.rank()
            }
        })
        .unwrap();
    let rank = if side == Color::White {
        pawn.rank() as i32 + 1
    } else {
        8 - pawn.rank() as i32
    };
    match (
        side,
        pawn_race(
            side,
            king(position, side),
            pawn,
            king(position, side.opponent()),
            position.side,
        ),
    ) {
        (Color::White, 1) => value.lower = value.lower.max(value.score.div_euclid(4) + 700),
        (Color::Black, 1) => value.upper = value.upper.min(value.score.div_euclid(4) - 700),
        (Color::White, -1) => value.upper = value.upper.min(11 - rank),
        (Color::Black, -1) => value.lower = value.lower.max(rank - 11),
        _ => (),
    }
    value
}

fn fortress_bound(side: Color, bound: i32, mut value: Bounded) -> Bounded {
    if side == Color::White {
        value.upper = value.upper.min(bound);
    } else {
        value.lower = value.lower.max(bound);
    }
    value
}

pub fn bishop_pawns(position: &Position, side: Color, value: Bounded) -> Bounded {
    let pawns = position.piece_squares(side, PieceKind::Pawn);
    let file = pawns[0].file();
    if !pawns.iter().all(|s| s.file() == file) {
        return value;
    }
    let pawn = *pawns
        .iter()
        .max_by_key(|s| {
            if side == Color::White {
                s.rank()
            } else {
                7 - s.rank()
            }
        })
        .unwrap();
    let forward = if side == Color::White { 1 } else { -1 };
    if [-1, 1].iter().any(|&df| {
        pawn.offset(df, forward).is_some_and(|s| {
            let p = position.board[s.0 as usize];
            !p.is_empty() && p.color() != side
        })
    }) {
        return value;
    }
    let flip = file >= 4;
    let p = Point::of(pawn, side, flip);
    let a = Point::of(king(position, side), side, flip);
    let k = Point::of(king(position, side.opponent()), side, flip);
    let b = Point::of(one(position, side, PieceKind::Bishop), side, flip);
    if p.f == 1 && (b.f + b.r) % 2 == 0 && k.f <= 2 && k.r > p.r && (a.r < k.r || a.f > 2) {
        fortress_bound(side, sign(side) * 2 * (9 - p.r), value)
    } else {
        value
    }
}

pub fn queen_pawn(position: &Position, side: Color, value: Bounded) -> Bounded {
    let pawn = one(position, side.opponent(), PieceKind::Pawn);
    let flip = pawn.file() >= 4;
    let p = Point::of(pawn, side, flip);
    let k = Point::of(king(position, side.opponent()), side, flip);
    let a = Point::of(king(position, side), side, flip);
    let q = Point::of(one(position, side, PieceKind::Queen), side, flip);
    let t = i32::from(position.side == side);
    let terminal = Point::new(p.f, 1);
    if p.r != 2
        || !(p.f == 1 || p.f == 3)
        || q == terminal
        || k.r > 3 - t
        || k.distance(p) > 2
        || (t == 1 && q.aligned(p) && !k.adjacent(p))
    {
        return value;
    }
    let effective = if k == terminal { 1 } else { t };
    if a.distance(p) - effective > if p.f == 1 { 3 } else { 2 } && a.distance(k) - effective > 2 {
        fortress_bound(side, (3 * value.score).div_euclid(32), value)
    } else {
        value
    }
}

pub fn rook_pawn(position: &Position, side: Color, score: i32) -> i32 {
    let pawn = one(position, side, PieceKind::Pawn);
    let flip = pawn.file() >= 4;
    let p = Point::of(pawn, side, flip);
    let r = Point::of(one(position, side, PieceKind::Rook), side, flip);
    let k = Point::of(king(position, side.opponent()), side, flip);
    let other = Point::of(one(position, side.opponent(), PieceKind::Rook), side, flip);
    if (p == Point::new(1, 7)
        && r == Point::new(1, 8)
        && other.f == 1
        && k.r == 7
        && (k.f == 7 || k.f == 8))
        || (k.distance(Point::new(p.f, 8)) < p.distance(Point::new(p.f, 8))
            && (p.r <= 4 || other.f > p.f + 3))
    {
        score.div_euclid(4)
    } else {
        score
    }
}

pub fn rook_against_pawns(position: &Position, side: Color, score: i32, checked: bool) -> i32 {
    if checked {
        return score;
    }
    for &pawn in position.piece_squares(side.opponent(), PieceKind::Pawn) {
        let enemy_king = king(position, side.opponent());
        let flip = enemy_king.file() < pawn.file();
        let p = Point::of(pawn, side, flip);
        let k = Point::of(enemy_king, side, flip);
        let a = Point::of(king(position, side), side, flip);
        let r = Point::of(one(position, side, PieceKind::Rook), side, flip);
        let terminal = Point::new(p.f, 1);
        let t = i32::from(position.side == side);
        let d = k.distance(terminal);
        let required = if d == 0 { 1 } else { d - 1 } + p.r - 1;
        let mut available = a.distance(terminal) - t - 1;
        if p.f < k.f && matches!((a.f - k.f, a.r - k.r), (2, 0) | (2, 1) | (1, 2) | (2, 2)) {
            available += 1;
        }
        if p.r <= 4 && r == Point::new(p.f + 2, 1) && k.adjacent(Point::new(p.f + 1, 2)) {
            available += 1;
        }
        if required <= available {
            return score.div_euclid(8);
        }
    }
    score
}

pub fn adjust(
    position: &Position,
    score: i32,
    endgame: u16,
    progress: i32,
    checked: bool,
    lower: i32,
    upper: i32,
) -> Bounded {
    let score = material_blend(position, score, endgame, progress);
    let mut result = Bounded {
        score,
        lower,
        upper,
    };
    let w = &position.counts[0];
    let b = &position.counts[1];
    if total(w) == 0
        || (w[0] == 0 && w[1] as u16 + w[2] as u16 == 1 && w[3] == 0 && w[4] == 0 && b[0] == 0)
    {
        result.upper = 0;
    }
    if total(b) == 0
        || (b[0] == 0 && b[1] as u16 + b[2] as u16 == 1 && b[3] == 0 && b[4] == 0 && w[0] == 0)
    {
        result.lower = 0;
    }
    let side = if score >= 0 {
        Color::White
    } else {
        Color::Black
    };
    let enemy = side.opponent();
    let own = &position.counts[side.index()];
    let other = &position.counts[enemy.index()];
    if own[0] > 0 && nonpawns(own) == 0 && total(other) == 0 {
        result = race_bounds(position, side, result);
    } else if own[0] > 0 && material(own) == (0, 1, 0, 0) {
        result = bishop_pawns(position, side, result);
    } else if own[0] == 1
        && material(own) == (0, 0, 1, 0)
        && other[0] == 0
        && material(other) == (0, 0, 1, 0)
    {
        result.score = rook_pawn(position, side, score);
    } else if own[0] == 0 && material(own) == (0, 0, 1, 0) && other[0] > 0 {
        result.score = rook_against_pawns(position, side, score, checked);
    } else if own[0] == 0 && material(own) == (0, 0, 0, 1) && other[0] == 1 && nonpawns(other) == 0
    {
        result = queen_pawn(position, side, result);
    }
    result.score = result.score.max(result.lower).min(result.upper);
    result
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Finished {
    pub adjusted_base: i32,
    pub late_score: i32,
    pub scaled_score: i32,
    pub score: i32,
    pub lower: i32,
    pub upper: i32,
}

/// White-relative subtotal after the root-owned preference and supplied identity.
/// Shared with diagnostic admission so the pre-endgame value has one producer.
#[inline]
pub fn adjusted_subtotal(
    base: i32,
    preference: i32,
    root_side: Color,
    range: u32,
    identity: u32,
) -> i32 {
    let variation = if range == 0 {
        0
    } else {
        (identity as u64 % (range as u64 + 1)) as i32 - (range / 2) as i32
    };
    base + sign(root_side) * preference + variation
}

pub fn finish(
    position: &Position,
    base: i32,
    preference: i32,
    root_side: Color,
    range: u32,
    identity: u32,
    endgame: u16,
    checked: bool,
    progress: i32,
) -> Finished {
    let adjusted_base = adjusted_subtotal(base, preference, root_side, range, identity);
    let late = if endgame >= 192 {
        adjust(
            position,
            adjusted_base,
            endgame,
            progress,
            checked,
            -10000,
            10000,
        )
    } else {
        Bounded {
            score: adjusted_base,
            lower: -10000,
            upper: 10000,
        }
    };
    let clipped = late.score.clamp(-7900, 7900);
    let h = position.halfmove as i64;
    let scaled_score = if h <= 11 {
        clipped
    } else {
        ((23 * (100 - h)).max(0) * clipped as i64 + 1024).div_euclid(2048) as i32
    };
    let (score, lower, upper) = if position.side == Color::White {
        (scaled_score, late.lower, late.upper)
    } else {
        (-scaled_score, -late.upper, -late.lower)
    };
    Finished {
        adjusted_base,
        late_score: late.score,
        scaled_score,
        score,
        lower,
        upper,
    }
}
