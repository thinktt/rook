fn king_pressure(position: &Position, defender: Color, marks: &Marks) -> i32 {
    let source = position.piece_squares(defender, PieceKind::King)[0];
    let attacker = defender.opponent();
    let counts = position.counts[attacker.index()];
    let mut pressure = 0;
    for (directions, mask, admitted) in [
        (
            &DIRECTIONS[4..],
            0xf0u8,
            counts[PieceKind::Rook.index()] != 0 || counts[PieceKind::Queen.index()] != 0,
        ),
        (
            &DIRECTIONS[..4],
            0xccu8,
            counts[PieceKind::Bishop.index()] != 0 || counts[PieceKind::Queen.index()] != 0,
        ),
    ] {
        if !admitted {
            continue;
        }
        for &step in directions {
            let mut cursor = source;
            while let Some(target) = cursor.offset(step.0, step.1) {
                let piece = position.board[target.0 as usize];
                if !piece.is_empty() && piece.color() == attacker {
                    break;
                }
                pressure += pressure_value(marks[attacker.index()][target.0 as usize] & mask);
                if !piece.is_empty() {
                    break;
                }
                cursor = target;
            }
        }
    }
    if counts[PieceKind::Knight.index()] != 0 {
        for step in KNIGHT {
            if let Some(target) = source.offset(step.0, step.1) {
                let piece = position.board[target.0 as usize];
                if piece.is_empty() || piece.color() == defender {
                    pressure += pressure_value(marks[attacker.index()][target.0 as usize] & 3);
                }
            }
        }
    }
    (pressure - 12).max(0)
}
