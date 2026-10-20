//! EVAL-KING-SHELTER. Activity pressure is a supplied produced dependency.
use crate::influence::Influence;
use crate::position::{Phase, Position};
use crate::types::{Color, Piece, PieceKind, Square};

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Shelter {
    pub terms: [i32; 2],
    pub weighted: i32,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Wing {
    Queenside,
    Kingside,
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Components {
    pub ring: i32,
    pub files: i32,
    pub screen: i32,
    pub shelter: i32,
}

const ROOK_FILE: [[u8; 3]; 7] = [
    [6, 6, 6],
    [10, 10, 6],
    [10, 10, 6],
    [10, 10, 6],
    [16, 16, 9],
    [22, 22, 12],
    [22, 22, 12],
];
const PAWN_FILE: [[u8; 3]; 7] = [
    [0, 0, 0],
    [8, 14, 18],
    [5, 8, 10],
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0],
];
const SCREEN: [i32; 13] = [-16, -12, -8, -4, 0, 4, 7, 10, 12, 13, 14, 14, 14];
const EXPOSURE: [[u8; 8]; 4] = [
    [0, 0, 3, 5, 5, 3, 0, 0],
    [0, 2, 6, 9, 9, 6, 2, 0],
    [5, 9, 13, 15, 15, 13, 9, 5],
    [12, 15, 18, 22, 22, 18, 15, 12],
];

pub fn compute(
    position: &Position,
    influence: &Influence,
    activity_pressure: [i32; 2],
    material_score: i32,
    weights: [i32; 2],
) -> Shelter {
    compute_with_phase(
        position,
        influence,
        activity_pressure,
        material_score,
        weights,
        position.phase(),
    )
}

/// Full evaluation may supply its already-produced current-position phase.
pub(crate) fn compute_with_phase(
    position: &Position,
    influence: &Influence,
    activity_pressure: [i32; 2],
    material_score: i32,
    weights: [i32; 2],
    phase: Phase,
) -> Shelter {
    debug_assert!(activity_pressure.iter().all(|p| *p >= 0));
    debug_assert!(weights.iter().all(|w| (0..=10_240).contains(w)));
    let mut terms = [0; 2];
    for color in [Color::White, Color::Black] {
        terms[color.index()] = compose(
            components(position, influence, color),
            activity_pressure[color.index()],
            phase,
        );
    }
    Shelter {
        terms,
        weighted: combine(terms, material_score, weights),
    }
}

#[inline]
fn relative_rank(color: Color, square: Square) -> u8 {
    if color == Color::White {
        square.rank()
    } else {
        7 - square.rank()
    }
}

#[inline]
fn relative_square(color: Color, file: u8, rank: u8) -> Square {
    Square(if color == Color::White {
        rank * 8 + file
    } else {
        (7 - rank) * 8 + file
    })
}

fn home_wing(color: Color, king: Square) -> Option<Wing> {
    match (relative_rank(color, king), king.file()) {
        (0, 0..=2) | (1, 0..=1) => Some(Wing::Queenside),
        (0, 5..=7) | (1, 6..=7) => Some(Wing::Kingside),
        _ => None,
    }
}

pub fn components(position: &Position, influence: &Influence, color: Color) -> Components {
    let king = position.piece_squares(color, PieceKind::King)[0];
    let wing = home_wing(color, king);
    Components {
        ring: ring(position, influence, color, king),
        files: wing.map_or(0, |wing| files(position, color, wing)),
        screen: screen(position, color, king),
        shelter: pattern_or_exposure(position, color, king, wing),
    }
}

fn ring(position: &Position, influence: &Influence, color: Color, king: Square) -> i32 {
    let mut sum = 0;
    for rank in -1..=1 {
        for file in -1..=1 {
            if rank == 0 && file == 0 {
                continue;
            }
            let Some(square) = king.offset(file, rank) else {
                continue;
            };
            let code = influence.code(color.opponent(), square);
            let weak = code & 1;
            let queen = (code >> 1) & 1;
            let rook = (code >> 2) & 3;
            let minor = (code >> 4) & 3;
            let pawn = code >> 6;
            let mut value = if queen == 0 {
                i32::from(rook & 1 != 0) * 14
                    + i32::from(rook >= 2) * 24
                    + i32::from(minor != 0) * 8
            } else {
                (if pawn != 0 || weak != 0 { 48 } else { 20 })
                    + i32::from(rook != 0 || minor != 0) * 18
            };
            if influence.code(color, square) >= 2 {
                value /= 2;
            }
            let occupant = position.board[square.0 as usize];
            if !occupant.is_empty() && occupant.color() == color {
                value = if occupant.kind() == PieceKind::Pawn {
                    value / 2
                } else {
                    3 * value / 4
                };
            }
            sum += value;
        }
    }
    (sum - 5).max(0)
}

fn files(position: &Position, color: Color, wing: Wing) -> i32 {
    let mut total = 0;
    for group in 0..3 {
        let file = if wing == Wing::Queenside {
            group
        } else {
            7 - group
        };
        for rank in 1..8 {
            let piece = position.board[relative_square(color, file, rank).0 as usize];
            if piece.is_empty() || piece.color() == color {
                continue;
            }
            match piece.kind() {
                PieceKind::Rook => total += ROOK_FILE[rank as usize - 1][group as usize] as i32,
                PieceKind::Pawn => {
                    total += PAWN_FILE[rank as usize - 1][group as usize] as i32;
                    break;
                }
                _ => {}
            }
        }
    }
    total
}

fn screen(position: &Position, color: Color, king: Square) -> i32 {
    let opponent = position.counts[color.opponent().index()];
    let has_queen = opponent[PieceKind::Queen.index()] != 0;
    if !has_queen && opponent[PieceKind::Rook.index()] == 0 {
        return 0;
    }
    let mut coverage = 0;
    let forward = if color == Color::White { 1 } else { -1 };
    for distance in 1..=2 {
        for file in -1..=1 {
            let Some(square) = king.offset(file, forward * distance) else {
                continue;
            };
            let piece = position.board[square.0 as usize];
            if !piece.is_empty()
                && piece.color() == color
                && matches!(
                    piece.kind(),
                    PieceKind::Pawn | PieceKind::Knight | PieceKind::Bishop
                )
            {
                coverage += (if file == 0 { 8 } else { 4 }) / distance as usize;
            }
        }
    }
    let value = SCREEN[coverage / 2];
    if has_queen {
        value
    } else {
        value.div_euclid(2)
    }
}

#[inline]
fn own_piece(position: &Position, color: Color, file: u8, rank: u8, kind: PieceKind) -> bool {
    position.board[relative_square(color, file, rank).0 as usize] == Piece::new(color, kind)
}

fn pattern_or_exposure(position: &Position, color: Color, king: Square, wing: Option<Wing>) -> i32 {
    if let Some(wing) = wing {
        let [left, center, right] = if wing == Wing::Kingside {
            [5, 6, 7]
        } else {
            [2, 1, 0]
        };
        if !own_piece(position, color, right, 0, PieceKind::Rook) {
            let mut word = 0u8;
            for (file, rank) in [(center, 2), (right, 2), (left, 1), (center, 1), (right, 1)] {
                word =
                    (word << 1) | u8::from(own_piece(position, color, file, rank, PieceKind::Pawn));
            }
            let bishop = |file, rank| own_piece(position, color, file, rank, PieceKind::Bishop);
            let rank = relative_rank(color, king);
            let file = king.file();
            let home_value = |l, c, r| {
                if rank != 0 {
                    0
                } else if file == left {
                    l
                } else if file == center {
                    c
                } else if file == right {
                    r
                } else {
                    0
                }
            };
            let additions = i32::from(bishop(right, 0)) * 8 + i32::from(bishop(center, 1)) * 14;
            let pattern = match word {
                0b00011 => 9,
                0b00110 => 13,
                0b00111 => home_value(15, 25, 14) + i32::from(bishop(left, 0)) * 4,
                0b01110 => {
                    (if rank == 1 && file == right {
                        3
                    } else {
                        home_value(10, 18, 12)
                    }) + i32::from(bishop(left, 0)) * 6
                }
                0b10001 => i32::from(bishop(center, 1)) * 5,
                0b10010 | 0b10011 | 0b11010 => 5,
                0b10100 => (additions - 4).max(0),
                0b10101 | 0b11100 => additions,
                0b10110 => 20,
                0b01101 => -10,
                _ => {
                    if word & (0b10000 | 0b00010) != 0 {
                        0
                    } else {
                        -10
                    }
                }
            };
            return if wing == Wing::Kingside {
                pattern
            } else {
                (3 * pattern).div_euclid(4)
            };
        }
    }
    let rank = relative_rank(color, king) as usize;
    let row = rank.min(7 - rank);
    let has_queen = position.counts[color.opponent().index()][PieceKind::Queen.index()] != 0;
    -(EXPOSURE[row][king.file() as usize] as i32) * if has_queen { 2 } else { 1 }
}

fn compose(parts: Components, activity_pressure: i32, phase: Phase) -> i32 {
    let opening = phase.opening as i64;
    let middle = phase.middlegame as i64;
    let end = phase.endgame as i64;
    let pressure_scale = (end + 2 * opening + 4 * middle) / 4;
    let shelter_scale = (opening / 2 - end + middle).max(0);
    let pressure = parts.ring as i64 / 2 + parts.files as i64 + activity_pressure as i64;
    (-pressure * pressure_scale
        + parts.screen as i64 * middle
        + parts.shelter as i64 * shelter_scale
        + 128)
        .div_euclid(256) as i32
}

fn combine(terms: [i32; 2], material_score: i32, weights: [i32; 2]) -> i32 {
    let material = material_score.clamp(-256, 256) as i64;
    let white = ((1024 + material) * weights[0] as i64 + 512).div_euclid(1024);
    let black = ((1024 - material) * weights[1] as i64 + 512).div_euclid(1024);
    (white * terms[0] as i64 - black * terms[1] as i64 + 512).div_euclid(1024) as i32
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sq(name: &str) -> Square {
        Square::parse(name).unwrap()
    }
    fn pos(pieces: &[(&str, char)]) -> Position {
        let mut cells = [' '; 64];
        for &(name, piece) in pieces {
            let index = sq(name).0 as usize;
            assert_eq!(cells[index], ' ');
            cells[index] = piece;
        }
        let mut placement = String::new();
        for rank in (0..8).rev() {
            if rank != 7 {
                placement.push('/');
            }
            let mut empty = 0;
            for file in 0..8 {
                let piece = cells[rank * 8 + file];
                if piece == ' ' {
                    empty += 1;
                } else {
                    if empty != 0 {
                        placement.push((b'0' + empty) as char);
                        empty = 0;
                    }
                    placement.push(piece);
                }
            }
            if empty != 0 {
                placement.push((b'0' + empty) as char);
            }
        }
        Position::from_fen(&format!("{placement} w - - 0 1")).unwrap()
    }
    fn influence() -> Influence {
        Influence {
            profiles: [[0; 64]; 2],
        }
    }

    #[test]
    fn neighborhood_uses_exact_digits_defense_then_occupancy_reductions() {
        let bare = pos(&[("d4", 'K'), ("h8", 'k')]);
        let mut map = influence();
        for (code, value) in [
            (4, 9),
            (8, 19),
            (12, 33),
            (16, 3),
            (2, 15),
            (66, 43),
            (3, 43),
            (6, 33),
            (18, 33),
            (70, 61),
        ] {
            map.profiles[1][sq("d5").0 as usize] = code;
            assert_eq!(
                ring(&bare, &map, Color::White, sq("d4")),
                value,
                "code {code}"
            );
        }
        map.profiles[1][sq("d5").0 as usize] = 70; // Unmodified value66.
        map.profiles[0][sq("d5").0 as usize] = 1;
        assert_eq!(ring(&bare, &map, Color::White, sq("d4")), 61); // Weak-only defense does not halve.
        map.profiles[0][sq("d5").0 as usize] = 2;
        assert_eq!(ring(&bare, &map, Color::White, sq("d4")), 28);
        let pawn = pos(&[("d4", 'K'), ("h8", 'k'), ("d5", 'P')]);
        assert_eq!(ring(&pawn, &map, Color::White, sq("d4")), 11); // floor(floor(66/2)/2)-5.
        let knight = pos(&[("d4", 'K'), ("h8", 'k'), ("d5", 'N')]);
        assert_eq!(ring(&knight, &map, Color::White, sq("d4")), 19);
    }

    #[test]
    fn home_wing_boundaries_and_file_scan_ignore_every_other_blocker() {
        for name in ["a1", "b1", "c1", "a2", "b2"] {
            assert_eq!(home_wing(Color::White, sq(name)), Some(Wing::Queenside));
        }
        for name in ["f1", "g1", "h1", "g2", "h2"] {
            assert_eq!(home_wing(Color::White, sq(name)), Some(Wing::Kingside));
        }
        for name in ["d1", "e1", "c2", "f2", "c3", "g3"] {
            assert_eq!(home_wing(Color::White, sq(name)), None);
        }
        let position = pos(&[
            ("b1", 'K'),
            ("h8", 'k'),
            ("a2", 'r'),
            ("a3", 'B'),
            ("a4", 'r'),
            ("a5", 'p'),
            ("a7", 'r'),
            ("b3", 'p'),
            ("c1", 'r'),
            ("c2", 'q'),
            ("c3", 'r'),
            ("c4", 'p'),
            ("c7", 'r'),
        ]);
        assert_eq!(files(&position, Color::White, Wing::Queenside), 46);
    }

    #[test]
    fn screen_has_piece_and_heavy_material_gates_and_separate_half_round() {
        let coverage = [
            ("d4", 'K'),
            ("a8", 'k'),
            ("h8", 'q'),
            ("c5", 'P'),
            ("d5", 'N'),
            ("e5", 'B'),
            ("c6", 'P'),
            ("d6", 'N'),
            ("e6", 'B'),
        ];
        let position = pos(&coverage);
        assert_eq!(screen(&position, Color::White, sq("d4")), 14);
        let mut rook_only = coverage;
        rook_only[2].1 = 'r';
        assert_eq!(screen(&pos(&rook_only), Color::White, sq("d4")), 7);
        assert_eq!(screen(&pos(&coverage[..2]), Color::White, sq("d4")), 0);
        assert_eq!(
            screen(
                &pos(&[("d4", 'K'), ("a8", 'k'), ("h8", 'q')]),
                Color::White,
                sq("d4")
            ),
            -16
        );
        assert_eq!(
            screen(
                &pos(&[("d4", 'K'), ("a8", 'k'), ("h8", 'r')]),
                Color::White,
                sq("d4")
            ),
            -8
        );
        let edge = pos(&[
            ("a1", 'K'),
            ("a8", 'k'),
            ("h8", 'r'),
            ("a2", 'P'),
            ("b2", 'N'),
            ("a3", 'B'),
            ("b3", 'P'),
        ]);
        assert_eq!(screen(&edge, Color::White, sq("a1")), 6); // Coverage18 ->13 ->floor(13/2).
        let excluded = pos(&[
            ("d4", 'K'),
            ("a8", 'k'),
            ("h8", 'q'),
            ("c5", 'R'),
            ("d5", 'Q'),
        ]);
        assert_eq!(screen(&excluded, Color::White, sq("d4")), -16);
    }

    #[test]
    fn pattern_king_slots_bishops_queenside_negative_floor_and_corner_gate() {
        for (king, value) in [("f1", 15), ("g1", 25), ("h1", 14)] {
            let position = pos(&[
                (king, 'K'),
                ("a8", 'k'),
                ("f2", 'P'),
                ("g2", 'P'),
                ("h2", 'P'),
            ]);
            assert_eq!(
                pattern_or_exposure(&position, Color::White, sq(king), Some(Wing::Kingside)),
                value
            );
        }
        let bishop = pos(&[
            ("g1", 'K'),
            ("a8", 'k'),
            ("f2", 'P'),
            ("g2", 'P'),
            ("h2", 'P'),
            ("f1", 'B'),
        ]);
        assert_eq!(
            pattern_or_exposure(&bishop, Color::White, sq("g1"), Some(Wing::Kingside)),
            29
        );
        let r2 = pos(&[
            ("h2", 'K'),
            ("a8", 'k'),
            ("h3", 'P'),
            ("f2", 'P'),
            ("g2", 'P'),
            ("f1", 'B'),
        ]);
        assert_eq!(
            pattern_or_exposure(&r2, Color::White, sq("h2"), Some(Wing::Kingside)),
            9
        );
        let negative = pos(&[
            ("b1", 'K'),
            ("h8", 'k'),
            ("a3", 'P'),
            ("c2", 'P'),
            ("a2", 'P'),
        ]);
        assert_eq!(
            pattern_or_exposure(&negative, Color::White, sq("b1"), Some(Wing::Queenside)),
            -8
        );
        let additions = pos(&[
            ("g1", 'K'),
            ("a8", 'k'),
            ("g3", 'P'),
            ("f2", 'P'),
            ("h1", 'B'),
            ("g2", 'B'),
        ]);
        assert_eq!(
            pattern_or_exposure(&additions, Color::White, sq("g1"), Some(Wing::Kingside)),
            18
        );
        for (corner, expected) in [('R', 0), ('B', 25), ('r', 25)] {
            let position = pos(&[
                ("g1", 'K'),
                ("a8", 'k'),
                ("f2", 'P'),
                ("g2", 'P'),
                ("h2", 'P'),
                ("h1", corner),
            ]);
            assert_eq!(
                pattern_or_exposure(&position, Color::White, sq("g1"), Some(Wing::Kingside)),
                expected
            );
        }
    }

    #[test]
    fn exposure_queen_doubling_phase_scales_and_material_weight_rounds() {
        let plain = pos(&[("e4", 'K'), ("a8", 'k')]);
        let queen = pos(&[("e4", 'K'), ("a8", 'k'), ("h8", 'q')]);
        assert_eq!(
            pattern_or_exposure(&plain, Color::White, sq("e4"), None),
            -22
        );
        assert_eq!(
            pattern_or_exposure(&queen, Color::White, sq("e4"), None),
            -44
        );
        let parts = Components {
            ring: 5,
            files: 1,
            screen: -16,
            shelter: -10,
        };
        let middle = Phase {
            opening: 0,
            middlegame: 256,
            endgame: 0,
        };
        let end = Phase {
            opening: 0,
            middlegame: 0,
            endgame: 256,
        };
        assert_eq!(compose(parts, 3, middle), -32);
        assert_eq!(compose(parts, 3, end), -1);
        assert_eq!(combine([-40, -20], 256, [1024, 1024]), -35);
        assert_eq!(
            combine([-40, -20], 100_000, [1024, 1024]),
            combine([-40, -20], 256, [1024, 1024])
        );
        assert_eq!(
            combine([-40, -20], -100_000, [10_240, 9173]),
            combine([-40, -20], -256, [10_240, 9173])
        );
    }

    #[test]
    fn complete_components_and_terms_reflect_color_without_retained_state() {
        for placement in [
            "r3k2r/pp1n1p2/2b1q1p1/3pP3/2BN1P2/1Q3N2/PP4PP/R3K2R",
            "7k/8/3n4/2B5/3R4/8/8/K7",
            "7k/8/8/8/8/8/8/K7",
        ] {
            let position = Position::from_fen(&format!("{placement} w - - 0 1")).unwrap();
            let influence = Influence::build(&position);
            let result = compute(&position, &influence, [57, 119], 217, [10_240, 8192]);
            assert_eq!(
                result,
                compute(&position, &influence, [57, 119], 217, [10_240, 8192])
            );
            let mut mirror = position;
            mirror.board = [Piece::EMPTY; 64];
            for (index, &piece) in position.board.iter().enumerate() {
                if !piece.is_empty() {
                    mirror.board[index ^ 56] = Piece::new(piece.color().opponent(), piece.kind());
                }
            }
            mirror.counts.swap(0, 1);
            mirror.squares.swap(0, 1);
            for side in 0..2 {
                for square in &mut mirror.squares[side] {
                    if square.0 < 64 {
                        square.0 ^= 56;
                    }
                }
            }
            mirror.side = position.side.opponent();
            mirror.recompute_derived();
            mirror.validate().unwrap();
            let reflected_influence = Influence::build(&mirror);
            assert_eq!(
                components(&position, &influence, Color::White),
                components(&mirror, &reflected_influence, Color::Black)
            );
            assert_eq!(
                components(&position, &influence, Color::Black),
                components(&mirror, &reflected_influence, Color::White)
            );
            let reflected = compute(
                &mirror,
                &reflected_influence,
                [119, 57],
                -217,
                [8192, 10_240],
            );
            assert_eq!(result.terms, [reflected.terms[1], reflected.terms[0]]);
        }
    }
}
