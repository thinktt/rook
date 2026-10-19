    #[test]
    fn pressure_tables_match_coordinate_owner_all_kings_blockers_and_complete_activity() {
        fn sparse(
            king: Square,
            defender: Color,
            admitted: &[PieceKind],
            blocker: Option<(Square, Color)>,
        ) -> Position {
            let mut board = [Piece::EMPTY; 64];
            board[king.0 as usize] = Piece::new(defender, PieceKind::King);
            if let Some((square, color)) = blocker {
                assert_ne!(square, king);
                board[square.0 as usize] = Piece::new(color, PieceKind::Knight);
            }
            let other = (0u8..64).map(Square).find(|square| {
                board[square.0 as usize].is_empty()
                    && (square.file().abs_diff(king.file()) >= 4
                        || square.rank().abs_diff(king.rank()) >= 4)
            }).unwrap();
            board[other.0 as usize] = Piece::new(defender.opponent(), PieceKind::King);
            for (index, &kind) in admitted.iter().enumerate() {
                let square = (0..64).map(|step| {
                    (king.0 as usize * 13 + index * 17 + step * 11) % 64
                }).find(|&square| board[square].is_empty()).unwrap();
                board[square] = Piece::new(defender.opponent(), kind);
            }
            let mut placement = String::new();
            for rank in (0..8).rev() {
                let mut empty = 0u8;
                for file in 0..8 {
                    let piece = board[rank * 8 + file];
                    if piece.is_empty() {
                        empty += 1;
                        continue;
                    }
                    if empty != 0 {
                        placement.push(char::from(b'0' + empty));
                        empty = 0;
                    }
                    let letter = match piece.kind() {
                        PieceKind::Pawn => 'p',
                        PieceKind::Knight => 'n',
                        PieceKind::Bishop => 'b',
                        PieceKind::Rook => 'r',
                        PieceKind::Queen => 'q',
                        PieceKind::King => 'k',
                    };
                    placement.push(if piece.color() == Color::White {
                        letter.to_ascii_uppercase()
                    } else {
                        letter
                    });
                }
                if empty != 0 { placement.push(char::from(b'0' + empty)); }
                if rank != 0 { placement.push('/'); }
            }
            Position::from_fen(&format!("{placement} {} - - 0 1",
                if defender == Color::White { "w" } else { "b" })).unwrap()
        }
        fn compare(pos: &Position, defender: Color) {
            for pattern in 0..6 {
                let mut marks = [[0; 64]; 2];
                for side in 0..2 {
                    for square in 0..64 {
                        marks[side][square] = match pattern {
                            0 => 0,
                            1 => 0x55,
                            2 => 0xaa,
                            3 => 0xff, // Weak and strong coexist, including marked a1 padding traps.
                            4 => (square as u8).wrapping_mul(73) ^ (side as u8 * 0x91),
                            _ => 1 << ((square + side) % 8),
                        };
                    }
                }
                assert_eq!(king_pressure(pos, defender, &marks),
                    coordinate_pressure(pos, defender, &marks),
                    "king={:?} defender={defender:?} pattern={pattern}",
                    pos.piece_squares(defender, PieceKind::King)[0]);
            }
        }

        let gates: &[&[PieceKind]] = &[
            &[], &[PieceKind::Knight], &[PieceKind::Bishop],
            &[PieceKind::Rook], &[PieceKind::Queen],
            &[PieceKind::Knight, PieceKind::Bishop, PieceKind::Rook, PieceKind::Queen],
        ];
        for defender in [Color::White, Color::Black] {
            for index in 0u8..64 {
                let king = Square(index);
                // Every king/edge/corner with absent and separately admitted classes.
                for admitted in gates {
                    compare(&sparse(king, defender, admitted, None), defender);
                }
                // Independent coordinate construction of blocker sites: tables are
                // used only by the owner under test, never by this placement/oracle.
                for (direction, step) in DIRECTIONS.iter().enumerate() {
                    let Some(first) = king.offset(step.0, step.1) else { continue; };
                    let blocker = if (index as usize + direction) % 2 == 0 {
                        first.offset(step.0, step.1).unwrap_or(first)
                    } else { first };
                    for color in [defender, defender.opponent()] {
                        compare(&sparse(king, defender,
                            &[PieceKind::Knight, PieceKind::Queen], Some((blocker, color))), defender);
                    }
                }
                // Exercise all on-board knight endpoints with each occupancy color.
                // This uses old coordinate offsets, not KNIGHT_SOURCES.
                for step in KNIGHT {
                    if let Some(blocker) = king.offset(step.0, step.1) {
                        for color in [defender, defender.opponent()] {
                            compare(&sparse(king, defender,
                                &[PieceKind::Knight, PieceKind::Queen], Some((blocker, color))), defender);
                        }
                    }
                }
            }
        }

        // Exact preserved baseline full wrapper uses the same unchanged native
        // numeric owners and the OLD coordinate pressure owner. Compare all
        // Activity fields, including R, rather than patching expected pressure
        // into the result of the production call itself.
        for placement in [
            "r3k2r/pp1n1p2/2b1q1p1/3pP3/2BN1P2/1Q3N2/PP4PP/R3K2R",
            "7k/8/3n4/2B5/3R4/8/8/K7",
            "7r/8/3P4/8/3Kp3/8/8/k7",
            "7k/8/8/8/8/8/8/K7",
        ] {
            let pos = position(placement);
            let mut custom = empty_influence();
            for side in 0..2 {
                for square in 0..64 {
                    custom.profiles[side][square] = (square as u8)
                        .wrapping_mul(73).wrapping_add(side as u8 * 91);
                }
            }
            for influence in [Influence::build(&pos), empty_influence(), custom] {
                for (material, weights) in [(217, [10_240, 8192]), (-400, [0, 1024])] {
                    let expected = coordinate_activity(&pos, &influence, material, weights);
                    assert_eq!(compute(&pos, &influence, material, weights), expected);
                }
            }
        }
    }
