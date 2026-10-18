pub use rook2::{influence, position, types};
#[allow(dead_code)]
#[path = "../oracle/influence.rs"]
mod old_influence;
#[allow(dead_code)]
#[path = "../oracle/activity.rs"]
mod old_activity;

#[cfg(test)]
mod tests {
    use super::*;
    use types::{Color, Piece, PieceKind};

    fn random(seed: &mut u64) -> u64 {
        *seed ^= *seed << 13;
        *seed ^= *seed >> 7;
        *seed ^= *seed << 17;
        *seed
    }

    #[test]
    fn valid_geometry_maps_activity_and_queries_match_coordinate_oracle() {
        let mut seed = 0x496d7032d1425aa9u64;
        for sample in 0..10_000 {
            let mut board = [Piece::EMPTY; 64];
            for side in [Color::White, Color::Black] {
                let population = 1 + random(&mut seed) % 16;
                let mut pawns = 0;
                for index in 0..population {
                    let kind = if index == 0 { PieceKind::King }
                               else { PieceKind::ALL[(random(&mut seed) % 5) as usize] };
                    if kind == PieceKind::Pawn && pawns == 8 { continue; }
                    let square = loop {
                        let square = (random(&mut seed) % 64) as usize;
                        if board[square].is_empty()
                            && (kind != PieceKind::Pawn || (8..56).contains(&square)) {
                            break square;
                        }
                    };
                    board[square] = Piece::new(side, kind);
                    if kind == PieceKind::Pawn { pawns += 1; }
                }
            }
            let mut placement = String::new();
            for rank in (0..8).rev() {
                if rank != 7 { placement.push('/'); }
                let mut empty = 0;
                for file in 0..8 {
                    let piece = board[rank*8+file];
                    if piece.is_empty() { empty += 1; }
                    else {
                        if empty != 0 { placement.push((b'0'+empty) as char); empty = 0; }
                        placement.push(piece.fen_char());
                    }
                }
                if empty != 0 { placement.push((b'0'+empty) as char); }
            }
            let turn = if sample % 2 == 0 { 'w' } else { 'b' };
            let fen = format!("{placement} {turn} - - 0 1");
            let pos = position::Position::from_fen(&fen).unwrap();
            let old = old_influence::Influence::build(&pos);
            let actual = influence::Influence::build(&pos);
            assert_eq!(actual.profiles, old.profiles, "influence {fen}");
            let weights = [(random(&mut seed)%10_241) as i32,(random(&mut seed)%10_241) as i32];
            let material = (random(&mut seed)%14_001) as i32-7000;
            let expected = old_activity::compute(&pos, &actual, material, weights);
            let actual = rook2::activity::compute(&pos, &actual, material, weights);
            assert_eq!((actual.pieces,actual.pressure,actual.weighted,actual.relation_queries),
                       (expected.pieces,expected.pressure,expected.weighted,expected.relation_queries),
                       "activity {fen} / {weights:?} / {material}");
        }
    }
}
