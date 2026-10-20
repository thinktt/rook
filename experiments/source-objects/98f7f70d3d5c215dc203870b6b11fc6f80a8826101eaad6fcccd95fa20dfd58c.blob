//! Current progress, ordered paths and selected pawn ending contributions.
use crate::influence::Influence;
use crate::pawn_structure::PawnStructure;
use crate::position::{Phase, Position};
use crate::types::{Color, Piece, PieceKind, Square};

pub fn distance(a: Square, b: Square) -> i32 {
    (a.file() as i32 - b.file() as i32)
        .abs()
        .max((a.rank() as i32 - b.rank() as i32).abs())
}

pub fn raw(position: &Position, map: &Influence, pawn: Square) -> i32 {
    raw_and_path::<false>(position, map, pawn).0
}

// Raw-only callers retain their scalar API; path collection is statically absent.
// Current selected candidates have the pawn's own color, so their two forward
// traversals can share each square's occupancy and normalized influence reads.
#[inline]
fn raw_and_path<const WITH_PATH: bool>(
    position: &Position,
    map: &Influence,
    pawn: Square,
) -> (i32, i32, bool) {
    const COEFFICIENT: [[i32; 8]; 6] = [
        [55, 60, 55, 50, 50, 55, 60, 55],
        [55, 60, 55, 50, 50, 55, 60, 55],
        [72, 78, 72, 65, 65, 72, 78, 72],
        [88, 96, 88, 80, 80, 88, 96, 88],
        [105, 114, 105, 95, 95, 105, 114, 105],
        [110, 120, 110, 100, 100, 110, 120, 110],
    ];
    let side = position.board[pawn.0 as usize].color();
    let forward = if side == Color::White { 1 } else { -1 };
    let rank = if side == Color::White {
        pawn.rank() + 1
    } else {
        8 - pawn.rank()
    };
    let mut measure = rank as i32 - 4;
    let mut next = pawn.offset(0, -forward);
    while let Some(square) = next {
        let piece = position.board[square.0 as usize];
        if !piece.is_empty() {
            measure += if piece.kind() == PieceKind::Rook {
                if piece.color() == side {
                    2
                } else {
                    -2
                }
            } else if piece.kind() == PieceKind::Queen && piece.color() != side {
                -1
            } else {
                0
            };
            break;
        }
        next = square.offset(0, -forward);
    }
    let mut path = 0;
    let mut protected = true;
    let mut next = pawn.offset(0, forward);
    while let Some(square) = next {
        let piece = position.board[square.0 as usize];
        if !piece.is_empty() && piece.kind() == PieceKind::Rook {
            measure += if piece.color() == side { -2 } else { 2 };
        }
        let own = map.code(side, square);
        let other = map.code(side.opponent(), square);
        if WITH_PATH {
            path += if piece.is_empty() { 1 } else { 2 };
            protected &= piece == Piece::new(side, PieceKind::King) || own != 0;
        }
        if own > other {
            measure += if square.rank() == 0 || square.rank() == 7 {
                2
            } else {
                1
            };
        } else {
            if own < other {
                measure -= 1;
            }
            if !piece.is_empty() && piece.color() != side {
                measure -= if square == pawn.offset(0, forward).unwrap() {
                    2
                } else {
                    1
                };
            }
        }
        next = square.offset(0, forward);
    }
    let preliminary =
        COEFFICIENT[rank as usize - 2][pawn.file() as usize] * (measure.max(-2) + 4) * 11 / 64;
    let raw = if map.code(side, pawn) >> 6 != 0 {
        preliminary * 11 / 8
    } else if map.code(side, pawn.offset(0, forward).unwrap()) >> 6 != 0 {
        preliminary * 10 / 8
    } else {
        preliminary
    };
    (raw, path, protected)
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Paths {
    pub score: i32,
    pub minimum: i32,
    pub best: i32,
    pub terminal: Option<Square>,
}
impl Default for Paths {
    fn default() -> Self {
        Self {
            score: 0,
            minimum: 100,
            best: 100,
            terminal: None,
        }
    }
}

pub fn candidates(position: &Position, map: &Influence, side: Color, pawns: &[Square]) -> Paths {
    let mut result = Paths::default();
    let (mut highest, mut second) = (0, 0);
    let king = position.piece_squares(side, PieceKind::King)[0];
    let enemy_king = position.piece_squares(side.opponent(), PieceKind::King)[0];
    let counts = position.counts[side.opponent().index()];
    let lone_rook = counts[1] == 0 && counts[2] == 0 && counts[3] == 1 && counts[4] == 0;
    let forward = if side == Color::White { 1 } else { -1 };
    let turn = i32::from(position.side == side);
    for &pawn in pawns {
        let rank = if side == Color::White {
            pawn.rank() + 1
        } else {
            8 - pawn.rank()
        };
        let terminal = Square(pawn.file() + if side == Color::White { 56 } else { 0 });
        let (raw, path, protected) = raw_and_path::<true>(position, map, pawn);
        let adjusted = 2 * path - if rank == 2 { 2 } else { 0 } - turn;
        let relation = 2 * distance(terminal, enemy_king) - adjusted - 2;
        let (multiplier, offset) = match relation {
            i32::MIN..=-2 => (54, 0),
            -1 => (59, 0),
            0 => (64, 0),
            1 => (70, 480),
            2 => (76, 960),
            _ => (83, 1440),
        };
        let intermediate = (raw * multiplier + offset) / 64;
        let king_distance =
            (2 * distance(king, pawn.offset(0, forward).unwrap()) - turn).clamp(1, 8);
        let mut score = (76 - 3 * king_distance) * intermediate / 64;
        if relation > 2
            && rank == 7
            && lone_rook
            && [-1, 1].iter().any(|&df| {
                pawn.offset(df, 0).is_some_and(|square| {
                    let piece = position.board[square.0 as usize];
                    piece == Piece::new(side, PieceKind::Pawn)
                        || (piece.is_empty()
                            && square.offset(0, -forward).is_some_and(|behind| {
                                position.board[behind.0 as usize]
                                    == Piece::new(side, PieceKind::Pawn)
                            }))
                })
            })
        {
            score += 400;
        }
        result.minimum = result.minimum.min(path);
        if (relation > 0 || protected) && adjusted < result.best {
            result.best = adjusted;
            result.terminal = Some(terminal);
        }
        if score > highest {
            second = highest;
            highest = score;
        } else if score > second {
            second = score;
        }
    }
    result.score = (16 * highest + 12 * second + 8) / 16;
    result
}

fn aligned(a: Square, b: Square) -> bool {
    let df = (a.file() as i32 - b.file() as i32).abs();
    let dr = (a.rank() as i32 - b.rank() as i32).abs();
    df == 0 || dr == 0 || df == dr
}

pub fn pawn_ending(position: &Position, map: &Influence, paths: [Paths; 2]) -> i32 {
    if paths[0].best == paths[1].best {
        return 0;
    }
    let leader = usize::from(paths[0].best > paths[1].best);
    let other = 1 - leader;
    let sign = if leader == 0 { 1 } else { -1 };
    if paths[other].best == 100 {
        return sign * 480;
    }
    let side = if other == 0 {
        Color::White
    } else {
        Color::Black
    };
    let terminal = paths[leader].terminal.unwrap();
    let enemy_terminal = paths[other].terminal.unwrap();
    if paths[other].best - paths[leader].best > 2
        || aligned(terminal, position.piece_squares(side, PieceKind::King)[0])
        || (aligned(terminal, enemy_terminal) && map.code(side, enemy_terminal) == 0)
    {
        sign * 400
    } else {
        0
    }
}

pub fn queen_ending(position: &Position, paths: [Paths; 2]) -> i32 {
    let w = paths[0].minimum;
    let b = paths[1].minimum;
    if w == 100 && b == 100 {
        return 0;
    }
    let difference = w - b;
    let score = match difference {
        i32::MIN..=-2 => 500 - 92 * w.min(5),
        -1 => 200 - 36 * w.min(5),
        0 => 0,
        1 => 36 * b.min(5) - 200,
        _ => 92 * b.min(5) - 500,
    } + if position.side == Color::White {
        20
    } else {
        -20
    };
    if difference == 0 {
        return score;
    }
    let pawns = position.counts[usize::from(difference > 0)][0];
    score
        / if pawns <= 1 {
            4
        } else if pawns == 2 {
            2
        } else {
            1
        }
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Progress {
    pub paths: [Paths; 2],
    pub ending: i32,
    pub weighted: i32,
}

/// Select surviving current pawns in retained descriptor order. Missing or
/// recolored squares are skipped; current pawns absent from the retained entry
/// are never appended. The fixed buffer covers the native eight-pawn capacity.
pub fn current_candidates(
    position: &Position,
    structure: &PawnStructure,
    side: Color,
    selected: &mut [Square; 8],
) -> usize {
    let mut len = 0;
    for descriptor in structure.pawn_slice(side) {
        if descriptor.candidate
            && position.board[descriptor.square.0 as usize] == Piece::new(side, PieceKind::Pawn)
        {
            selected[len] = descriptor.square;
            len += 1;
        }
    }
    len
}

pub fn selected(
    position: &Position,
    map: &Influence,
    structure: &PawnStructure,
    phase: Phase,
    material: i32,
    weights: [i32; 2],
) -> Progress {
    let mut paths = [Paths::default(); 2];
    let mut lengths = [0; 2];
    for side in [Color::White, Color::Black] {
        let mut selected = [Square(0); 8];
        let len = current_candidates(position, structure, side, &mut selected);
        lengths[side.index()] = len;
        paths[side.index()] = candidates(position, map, side, &selected[..len]);
    }
    let ending = ending(position, map, paths, lengths[0] + lengths[1] != 0);
    let ending = fallback(position, ending);
    Progress {
        paths,
        ending,
        weighted: weighted(
            phase,
            material,
            weights,
            [paths[0].score, paths[1].score],
            ending,
        ),
    }
}

pub fn ending(position: &Position, map: &Influence, paths: [Paths; 2], nonempty: bool) -> i32 {
    let mut ending = 0;
    if nonempty {
        if position
            .counts
            .iter()
            .all(|c| c[1..5].iter().all(|&n| n == 0))
        {
            ending = pawn_ending(position, map, paths);
        } else if position
            .counts
            .iter()
            .all(|c| c[1] == 0 && c[2] == 0 && c[3] == 0 && c[4] == 1)
        {
            ending = queen_ending(position, paths);
        }
    }
    ending
}

pub fn structure_weighted(
    phase: Phase,
    structure: [i32; 2],
    pieces: [i32; 2],
    weights: [i32; 2],
) -> i32 {
    let first = ((structure[0] - pieces[1]) as i64 * weights[0] as i64
        - (structure[1] - pieces[0]) as i64 * weights[1] as i64
        + 512)
        .div_euclid(1024);
    (first * (13 * phase.opening as i64 + 14 * phase.middlegame as i64 + 19 * phase.endgame as i64)
        + 2048)
        .div_euclid(4096) as i32
}

pub fn fallback(position: &Position, ending: i32) -> i32 {
    if ending != 0
        || position
            .counts
            .iter()
            .any(|c| c[1..5].iter().any(|&n| n != 0))
    {
        return ending;
    }
    let d = position.counts[0][0] as i32 - position.counts[1][0] as i32;
    d.signum() * if d.abs() >= 2 { 160 } else { 100 }
}

pub fn weighted(
    phase: Phase,
    material: i32,
    weights: [i32; 2],
    scores: [i32; 2],
    ending: i32,
) -> i32 {
    let m = material.clamp(-256, 256) as i64;
    let w = ((1024 - m) * weights[0] as i64 + 512).div_euclid(1024);
    let b = ((1024 + m) * weights[1] as i64 + 512).div_euclid(1024);
    let balance =
        (w * scores[0] as i64 - b * scores[1] as i64 + 512).div_euclid(1024) + ending as i64;
    (balance * (phase.middlegame as i64 + 2 * phase.endgame as i64) + 256).div_euclid(512) as i32
}

#[cfg(test)]
mod tests {
    use super::*;

    fn separate_raw_reference(position: &Position, map: &Influence, pawn: Square) -> i32 {
        const COEFFICIENT: [[i32; 8]; 6] = [
            [55, 60, 55, 50, 50, 55, 60, 55],
            [55, 60, 55, 50, 50, 55, 60, 55],
            [72, 78, 72, 65, 65, 72, 78, 72],
            [88, 96, 88, 80, 80, 88, 96, 88],
            [105, 114, 105, 95, 95, 105, 114, 105],
            [110, 120, 110, 100, 100, 110, 120, 110],
        ];
        let side = position.board[pawn.0 as usize].color();
        let forward = if side == Color::White { 1 } else { -1 };
        let rank = if side == Color::White {
            pawn.rank() + 1
        } else {
            8 - pawn.rank()
        };
        let mut measure = rank as i32 - 4;
        let mut next = pawn.offset(0, -forward);
        while let Some(square) = next {
            let piece = position.board[square.0 as usize];
            if !piece.is_empty() {
                measure += if piece.kind() == PieceKind::Rook {
                    if piece.color() == side {
                        2
                    } else {
                        -2
                    }
                } else if piece.kind() == PieceKind::Queen && piece.color() != side {
                    -1
                } else {
                    0
                };
                break;
            }
            next = square.offset(0, -forward);
        }
        let mut next = pawn.offset(0, forward);
        while let Some(square) = next {
            let piece = position.board[square.0 as usize];
            if !piece.is_empty() && piece.kind() == PieceKind::Rook {
                measure += if piece.color() == side { -2 } else { 2 };
            }
            let own = map.code(side, square);
            let other = map.code(side.opponent(), square);
            if own > other {
                measure += if square.rank() == 0 || square.rank() == 7 {
                    2
                } else {
                    1
                };
            } else {
                if own < other {
                    measure -= 1;
                }
                if !piece.is_empty() && piece.color() != side {
                    measure -= if square == pawn.offset(0, forward).unwrap() {
                        2
                    } else {
                        1
                    };
                }
            }
            next = square.offset(0, forward);
        }
        let preliminary =
            COEFFICIENT[rank as usize - 2][pawn.file() as usize] * (measure.max(-2) + 4) * 11 / 64;
        if map.code(side, pawn) >> 6 != 0 {
            preliminary * 11 / 8
        } else if map.code(side, pawn.offset(0, forward).unwrap()) >> 6 != 0 {
            preliminary * 10 / 8
        } else {
            preliminary
        }
    }
    // Coordinate-indexed path oracle: independent of the fused offset loop.
    fn separate_path_reference(position: &Position, map: &Influence, pawn: Square) -> (i32, bool) {
        let side = position.board[pawn.0 as usize].color();
        let mut path = 0;
        let mut protected = true;
        for rank in 0..8 {
            let ahead = if side == Color::White { rank > pawn.rank() }
                        else { rank < pawn.rank() };
            if !ahead { continue; }
            let square = Square(8 * rank + pawn.file());
            let piece = position.board[square.0 as usize];
            path += if piece.is_empty() { 1 } else { 2 };
            protected &= piece == Piece::new(side, PieceKind::King) || map.code(side, square) != 0;
        }
        (path, protected)
    }

    #[test]
    fn shared_scan_matches_separate_raw_and_coordinate_path_across_both_colors() {
        // Occupied forward squares never stop either scan, own kings protect
        // without influence, and the nearer knight hides the backward rook.
        // Relative ranks2,4,7 cover the long path and immediate promotion edge.
        for (placement, pawn) in [
            ("3K3k/3r4/3R4/3p4/3P4/8/3R4/8", "d4"),
            ("3K3k/3r4/3R4/3p4/3P4/3N4/3R4/8", "d4"),
            ("8/3r4/8/3p4/3P4/3r4/3R4/3k3K", "d5"),
            ("8/3r4/3n4/3p4/3P4/3r4/3R4/3k3K", "d5"),
            ("K6k/r7/8/R7/8/p7/P7/R7", "a2"),
            ("5r1k/5P2/8/8/8/8/8/5K2", "f7"),
            ("5k2/8/8/8/8/8/5p2/5R1K", "f2"),
        ] {
            let position = Position::from_fen(&format!("{placement} w - - 0 1")).unwrap();
            let pawn = Square::parse(pawn).unwrap();
            let check = |map: &Influence| {
                let raw = separate_raw_reference(&position, map, pawn);
                let (path, protected) = separate_path_reference(&position, map, pawn);
                assert_eq!(raw_and_path::<true>(&position, map, pawn), (raw, path, protected));
                assert_eq!(super::raw(&position, map, pawn), raw);
            };
            check(&Influence::build(&position));
            // Exercise all normalized profile byte values, including carries,
            // equality, both ordinal comparisons and current/front pawn bits.
            // These are internal pure-producer witnesses, not admission claims
            // that every constructed map is placement-derived.
            for value in 0..=255u16 {
                let mut map = Influence { profiles: [[0; 64]; 2] };
                for square in 0..64 {
                    map.profiles[0][square] = (value as u8).wrapping_add((37 * square) as u8);
                    map.profiles[1][square] = (value as u8).wrapping_mul(73)
                        .wrapping_add((13 * square) as u8);
                }
                check(&map);
            }
        }
    }
}
