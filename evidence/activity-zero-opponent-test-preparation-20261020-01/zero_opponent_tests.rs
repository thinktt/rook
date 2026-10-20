//! Independent source-support controls. No production profile_sum/relation oracle.
use super::{compute, piece_score_kind, Mobility};
use crate::influence::Influence;
use crate::position::Position;
use crate::types::{Color, PieceKind, Square};

// Decode the five normalized digits by division/remainder, without the
// production masks or the proposed opponent-zero branch.
fn normalized_sum(mut byte: u8) -> i64 {
    let mut sum = 0;
    for radix in [2u8, 2, 4, 4, 4] {
        sum += i64::from(byte % radix);
        byte /= radix;
    }
    assert_eq!(byte, 0);
    sum
}

fn old_support_penalty(own: u8, opponent: u8) -> i64 {
    let opposing_count = normalized_sum(opponent);
    if normalized_sum(own) <= opposing_count { 5 * opposing_count + 2 } else { 0 }
}

fn supplied(color: Color, source: Square, own: u8, opponent: u8) -> Influence {
    let mut map = Influence { profiles: [[0; 64]; 2] };
    map.profiles[color.index()][source.0 as usize] = own;
    map.profiles[color.opponent().index()][source.0 as usize] = opponent;
    map
}

fn exhaustive_kind<const KIND: usize>() {
    let source = Square::parse("d4").unwrap();
    for own in 0u16..=255 {
        for opponent in 0u16..=255 {
            let expected = (-old_support_penalty(own as u8, opponent as u8), 17);
            for color in [Color::White, Color::Black] {
                let map = supplied(color, source, own as u8, opponent as u8);
                // T=0 makes the curve input0 for every kind/phase; C=3
                // suppresses low mobility, independently isolating support.
                let actual = piece_score_kind::<KIND>(&map, color, source,
                    Mobility { categories: 3, total: 0, queries: 17 }, 256);
                assert_eq!(actual, expected, "kind={KIND} color={color:?} own={own} opponent={opponent}");
            }
        }
    }
}

#[test]
fn experiment53_all_profile_pairs_preserve_uncapped_support_for_every_kind() {
    assert_eq!(old_support_penalty(0, 0), 2);
    assert_eq!(old_support_penalty(120, 104), 0); // Six vs five, not both capped4.
    assert_eq!(old_support_penalty(255, 255), 57); // All five normalized digits.
    exhaustive_kind::<1>();
    exhaustive_kind::<2>();
    exhaustive_kind::<3>();
    exhaustive_kind::<4>();
}

fn low_mobility_kind<const KIND: usize>() {
    for color in [Color::White, Color::Black] {
        // Literal LOW-MOBILITY values from released relative-square table.
        for (white, black, square_penalty, knight_region) in [
            ("c4", "c5", 5, true),
            ("c7", "c2", 10, false),
            ("d7", "d2", 9, true),
        ] {
            let source = Square::parse(if color == Color::White { white } else { black }).unwrap();
            for (own, opponent) in [(0, 0), (1, 0), (16, 0), (64, 0), (0, 255)] {
                let map = supplied(color, source, own, opponent);
                for categories in 0i64..=3 {
                    // Only a normalized pawn digit grants the knight exemption.
                    let exempt = KIND == 1 && own / 64 != 0 && knight_region;
                    let active = categories < 3 && !exempt;
                    let queried = active && categories < 2;
                    let mut penalty = if active { square_penalty * (3 - categories) } else { 0 };
                    // These supplied cases have either opponent0 (favorable)
                    // or own0/opponent255 (unfavorable for every tested kind).
                    if queried && opponent != 0 {
                        penalty += 6 + if categories == 0 { 15 } else { 0 };
                    }
                    let expected = (-old_support_penalty(own, opponent) - penalty,
                        17 + u64::from(queried));
                    let actual = piece_score_kind::<KIND>(&map, color, source,
                        Mobility { categories, total: 0, queries: 17 }, 0);
                    assert_eq!(actual, expected,
                        "kind={KIND} color={color:?} source={source} own={own} opponent={opponent} C={categories}");
                }
            }
        }
    }
}

#[test]
fn experiment53_source_queries_and_knight_exemption_remain_live() {
    low_mobility_kind::<1>();
    low_mobility_kind::<2>();
    low_mobility_kind::<3>();
    low_mobility_kind::<4>();
}

// Build a valid FEN with one active piece and eight friendly pawn blockers.
// Geometry is independent coordinate arithmetic, not Activity's target tables.
fn blocked_position(kind: PieceKind, color: Color) -> (Position, Square) {
    let source = Square::parse(if color == Color::White { "c4" } else { "c5" }).unwrap();
    let mut board = [' '; 64];
    board[0] = 'K';
    board[63] = 'k';
    let piece = match kind {
        PieceKind::Knight => 'N', PieceKind::Bishop => 'B',
        PieceKind::Rook => 'R', PieceKind::Queen => 'Q', _ => unreachable!(),
    };
    board[source.0 as usize] = if color == Color::White { piece } else { piece.to_ascii_lowercase() };
    let steps = if kind == PieceKind::Knight {
        [(1i8, 2i8), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
    } else {
        [(1i8, 1i8), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
    };
    for (df, dr) in steps {
        let file = (source.0 % 8) as i8 + df;
        let rank = (source.0 / 8) as i8 + dr;
        assert!((0..8).contains(&file) && (1..7).contains(&rank));
        let index = rank as usize * 8 + file as usize;
        assert_eq!(board[index], ' ');
        board[index] = if color == Color::White { 'P' } else { 'p' };
    }
    let mut fen = String::new();
    for rank in (0usize..8).rev() {
        let mut empty = 0;
        for file in 0usize..8 {
            let piece = board[8 * rank + file];
            if piece == ' ' { empty += 1; }
            else {
                if empty != 0 { fen.push(char::from(b'0' + empty)); empty = 0; }
                fen.push(piece);
            }
        }
        if empty != 0 { fen.push(char::from(b'0' + empty)); }
        if rank != 0 { fen.push('/'); }
    }
    fen.push_str(if color == Color::White { " w - - 0 1" } else { " b - - 0 1" });
    (Position::from_fen(&fen).unwrap(), source)
}

#[test]
fn experiment53_full_activity_custom_sources_preserve_score_pressure_and_work() {
    for color in [Color::White, Color::Black] {
        for kind in [PieceKind::Knight, PieceKind::Bishop, PieceKind::Rook, PieceKind::Queen] {
            let (position, source) = blocked_position(kind, color);
            assert_eq!(position.counts[color.index()][kind.index()], 1);
            for (own, opponent) in [(0, 0), (1, 0), (16, 0), (64, 0), (0, 255)] {
                let map = supplied(color, source, own, opponent);
                let result = compute(&position, &map, 0, [1024, 1024]);
                // All destinations blocked by friendly opaque pawns: C=T=0,
                // no marks or destination relation queries. Source P(c4)=5.
                let exempt = kind == PieceKind::Knight && own / 64 != 0;
                let mut raw = -old_support_penalty(own, opponent);
                if !exempt {
                    raw -= 15;
                    if opponent != 0 { raw -= 21; } // Own0 vs opponent255.
                }
                let mut expected_pieces = [0; 2];
                expected_pieces[color.index()] = (276i64 * raw + 128).div_euclid(256) as i32;
                assert_eq!(result.pieces, expected_pieces, "kind={kind:?} color={color:?} own={own} opponent={opponent}");
                assert_eq!(result.pressure, [0, 0]);
                assert_eq!(result.relation_queries, u64::from(!exempt));
                // At material0 and weights1024, personality composition first
                // leaves the signed piece difference exact, before phase scale.
                let phase = position.phase();
                let scale = i64::from(phase.opening) + 2 * i64::from(phase.middlegame) + i64::from(phase.endgame);
                let difference = i64::from(expected_pieces[0]) - i64::from(expected_pieces[1]);
                let expected_weighted = (9 * difference * scale + 2048).div_euclid(4096) as i32;
                assert_eq!(result.weighted, expected_weighted);
            }
        }
    }
}
