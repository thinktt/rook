//! Cold setup/transition schemas; placement and transitions use the native kernel.
use super::{array, color, object, text, Result};
use rook2::{
    movegen::{self, MoveList},
    position::{
        Phase, Position, BLACK_KINGSIDE, BLACK_QUEENSIDE, NO_SQUARE, WHITE_KINGSIDE,
        WHITE_QUEENSIDE,
    },
    types::{Color, MoveKind, Piece, PieceKind, Square},
};
use serde_json::{json, Map, Value};

const COLORS: [&str; 2] = ["white", "black"];
const KINDS: [&str; 6] = ["pawn", "knight", "bishop", "rook", "queen", "king"];

pub(super) fn square(v: &Value) -> Result<Square> {
    Square::parse(text(v)?).ok_or_else(|| "expected lowercase algebraic square".into())
}

fn bounded_material(position: &Position) -> Result<()> {
    for counts in position.counts {
        if counts[1..4].iter().any(|&count| count > 10) || counts[4] > 9 {
            return Err("placement exceeds bounded diagnostic piece-type counts".into());
        }
    }
    Ok(())
}

pub(super) fn placement(value: &Value, bounded: bool) -> Result<Position> {
    let position = Position::from_fen(&format!("{} w - - 0 1", text(value)?))?;
    if bounded {
        bounded_material(&position)?;
    }
    Ok(position)
}

fn rights(position: &Position) -> String {
    let mut result = String::new();
    for (name, bit) in [
        ('K', WHITE_KINGSIDE),
        ('Q', WHITE_QUEENSIDE),
        ('k', BLACK_KINGSIDE),
        ('q', BLACK_QUEENSIDE),
    ] {
        if position.rights & bit != 0 {
            result.push(name);
        }
    }
    if result.is_empty() {
        result.push('-');
    }
    result
}

fn ep(position: &Position) -> String {
    if position.ep == NO_SQUARE {
        "-".into()
    } else {
        Square(position.ep).to_string()
    }
}

fn piece_order(position: &Position) -> Value {
    let mut result = Map::new();
    for (index, side) in [Color::White, Color::Black].into_iter().enumerate() {
        let mut pieces = Map::new();
        for (kind, name) in PieceKind::ALL.into_iter().zip(KINDS) {
            pieces.insert(
                name.into(),
                json!(position
                    .piece_squares(side, kind)
                    .iter()
                    .map(ToString::to_string)
                    .collect::<Vec<_>>()),
            );
        }
        result.insert(COLORS[index].into(), Value::Object(pieces));
    }
    Value::Object(result)
}

fn identity(position: &Position) -> Value {
    json!({"primary":position.primary,"secondary":position.secondary,"pawn":position.pawn,"pawnGroup":position.pawn % 128})
}

pub(super) fn phase_value(phase: Phase) -> Value {
    json!({"opening":phase.opening,"middlegame":phase.middlegame,"endgame":phase.endgame})
}

fn state(position: &Position) -> Value {
    json!({"placement":position.placement(),"sideToMove":COLORS[position.side.index()],
           "castling":rights(position),"enPassant":ep(position),"halfmoveClock":position.halfmove,
           "pieceOrder":piece_order(position),"identity":identity(position),"phase":phase_value(position.phase())})
}

fn restore_order(position: &mut Position, value: &Value) -> Result<()> {
    object(value, &COLORS)?;
    for (index, side) in [Color::White, Color::Black].into_iter().enumerate() {
        let groups = &value[COLORS[index]];
        object(groups, &KINDS)?;
        let mut cursor = 0;
        let mut seen = 0u64;
        for (kind, name) in PieceKind::ALL.into_iter().zip(KINDS) {
            let group = array(&groups[name], 0, 16)?;
            if group.len() != position.counts[index][kind.index()] as usize {
                return Err("piece order must contain every matching piece exactly once".into());
            }
            for item in group {
                let square = square(item)?;
                if position.board[square.0 as usize] != Piece::new(side, kind)
                    || seen & (1u64 << square.0) != 0
                {
                    return Err("piece order has a duplicate or mismatched square".into());
                }
                seen |= 1u64 << square.0;
                position.squares[index][cursor] = square;
                cursor += 1;
            }
        }
    }
    position.validate()
}

fn sequence_position(fen: &str, normalize: bool) -> Result<Position> {
    let mut position = Position::from_fen(fen)?;
    bounded_material(&position)?;
    if !normalize {
        // Lower moveSequence receives already-established rule state. FEN
        // syntax/target occupancy were validated by the native parser, but its
        // setup normalization must not replace these supplied flags.
        let fields: Vec<_> = fen.split(' ').collect();
        position.rights = fields[2].bytes().fold(0, |bits, name| {
            bits | match name {
                b'K' => WHITE_KINGSIDE,
                b'Q' => WHITE_QUEENSIDE,
                b'k' => BLACK_KINGSIDE,
                b'q' => BLACK_QUEENSIDE,
                _ => 0,
            }
        });
        position.ep = if fields[3] == "-" {
            NO_SQUARE
        } else {
            Square::parse(fields[3]).unwrap().0
        };
    }
    // Lower moveSequence supplies a legal established move state. Setup history
    // starts in the broader POSITION-SETUP domain: it can initially attack the
    // nonmoving king, while every played move must preserve its own king.
    if !normalize && movegen::in_check(&position, position.side.opponent()) {
        return Err("nonmoving king is attacked in the initial move state".into());
    }
    Ok(position)
}

fn advance(position: &Position, spelling: &str) -> Result<Position> {
    if !spelling.is_ascii()
        || !matches!(spelling.len(), 4 | 5)
        || Square::parse(&spelling[..2]).is_none()
        || Square::parse(&spelling[2..4]).is_none()
        || (spelling.len() == 5 && !matches!(spelling.as_bytes()[4], b'n' | b'b' | b'r' | b'q'))
    {
        return Err("malformed coordinate move".into());
    }
    let mut legal = MoveList::new();
    movegen::generate_legal(position, &mut legal);
    let movement = legal
        .as_slice()
        .iter()
        .copied()
        .find(|mv| mv.to_string() == spelling)
        .ok_or_else(|| format!("illegal move: {spelling}"))?;
    if movement.kind() == MoveKind::EnPassant {
        let required_rank = if position.side == Color::White { 5 } else { 2 };
        let victim = if position.side == Color::White {
            movement.to().0 - 8
        } else {
            movement.to().0 + 8
        };
        if movement.to().rank() != required_rank
            || position.board[victim as usize]
                != Piece::new(position.side.opponent(), PieceKind::Pawn)
        {
            return Err(
                "move sequence requires ordinary en-passant geometry and pawn victim".into(),
            );
        }
    }
    let child = position.played_unchecked(movement);
    bounded_material(&child)?;
    Ok(child)
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    match operation {
        "position.setup" => {
            object(input, &["queries"])?;
            let mut results = Vec::new();
            for query in array(&input["queries"], 1, 4096)? {
                object(query, &["placement", "sideToMove", "castling", "enPassant"])?;
                let side = color(&query["sideToMove"])?;
                let position = Position::from_fen(&format!(
                    "{} {} {} {} 0 1",
                    text(&query["placement"])?,
                    if side == Color::White { "w" } else { "b" },
                    text(&query["castling"])?,
                    text(&query["enPassant"])?
                ))?;
                let mut sequences = Map::new();
                for (index, side) in [Color::White, Color::Black].into_iter().enumerate() {
                    let king = position.piece_squares(side, PieceKind::King)[0];
                    let mut sequence = vec![king.to_string()];
                    for square in 0..64 {
                        let piece = position.board[square];
                        if !piece.is_empty()
                            && piece.color() == side
                            && piece.kind() != PieceKind::King
                        {
                            sequence.push(Square(square as u8).to_string());
                        }
                    }
                    sequences.insert(COLORS[index].into(), json!(sequence));
                }
                results.push(json!({"placement":query["placement"],"sideToMove":query["sideToMove"],
                    "castling":rights(&position),"enPassant":ep(&position),"pieceSequence":sequences,
                    "pieceOrder":piece_order(&position)}));
            }
            Ok(json!({"results":results}))
        }
        "position.setupMoveSequence" | "position.moveSequence" => {
            let normalize = operation == "position.setupMoveSequence";
            let (fen, mut position) = if normalize {
                object(input, &["fen", "moves"])?;
                let fen = text(&input["fen"])?;
                (fen, sequence_position(fen, true)?)
            } else {
                object(input, &["initial", "moves"])?;
                object(&input["initial"], &["fen", "pieceOrder"])?;
                let fen = text(&input["initial"]["fen"])?;
                let mut position = sequence_position(fen, false)?;
                restore_order(&mut position, &input["initial"]["pieceOrder"])?;
                (fen, position)
            };
            let mut initial = state(&position);
            initial["placement"] = json!(fen.split(' ').next().unwrap());
            let mut results = vec![initial];
            for movement in array(&input["moves"], 1, 256)? {
                position = advance(&position, text(movement)?)?;
                results.push(state(&position));
            }
            Ok(json!({"results":results}))
        }
        "position.identity" => {
            object(input, &["queries"])?;
            let mut results = Vec::new();
            for query in array(&input["queries"], 1, 4096)? {
                object(query, &["placement"])?;
                results.push(identity(&placement(&query["placement"], true)?));
            }
            Ok(json!({"results":results}))
        }
        "evaluation.phase" => {
            object(input, &["placement"])?;
            Ok(phase_value(placement(&input["placement"], false)?.phase()))
        }
        _ => Err("unknown position operation".into()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn raw_move_state_and_setup_normalization_are_distinct() {
        let fen = "7k/8/8/8/8/8/8/K7 w KQ e6 255 1";
        let raw = sequence_position(fen, false).unwrap();
        let setup = sequence_position(fen, true).unwrap();
        assert_eq!((rights(&raw), ep(&raw)), ("KQ".into(), "e6".into()));
        assert_eq!((rights(&setup), ep(&setup)), ("-".into(), "-".into()));
        assert_eq!(advance(&raw, "a1b1").unwrap().halfmove, 0);
    }

    #[test]
    fn diagnostic_ep_rejects_the_broader_joined_nonpawn_transition() {
        let position = sequence_position("7k/8/8/3nP3/8/8/8/K7 w - d6 0 1", false).unwrap();
        let mut native = MoveList::new();
        movegen::generate_legal(&position, &mut native);
        assert!(native
            .as_slice()
            .iter()
            .any(|mv| mv.kind() == MoveKind::EnPassant));
        assert!(advance(&position, "e5d6").is_err());
        assert!(advance(&position, "e5e6").is_ok());
    }

    #[test]
    fn placement_domains_keep_promotion_heavy_phase_and_setup_admitted() {
        let heavy = "7k/8/8/8/8/NNNNNNNN/NNN5/K7";
        assert!(placement(&json!(heavy), false).is_ok());
        assert!(placement(&json!(heavy), true).is_err());
        let duplicate = json!({"white":{"pawn":["a2","a2"],"knight":[],"bishop":[],"rook":[],"queen":[],"king":["a1"]},
                              "black":{"pawn":[],"knight":[],"bishop":[],"rook":[],"queen":[],"king":["h8"]}});
        let mut position = placement(&json!("7k/8/8/8/8/8/PP6/K7"), false).unwrap();
        assert!(restore_order(&mut position, &duplicate).is_err());
    }
    #[test]
    fn sequence_capacity_includes_continuation_after_draw_thresholds() {
        let moves: Vec<_> = ["a1b1", "h8g8", "b1a1", "g8h8"]
            .into_iter()
            .cycle()
            .take(256)
            .collect();
        let mut input = json!({"fen":"7k/8/8/8/8/8/8/K7 w - - 0 1","moves":moves});
        let output = dispatch("position.setupMoveSequence", &input).unwrap();
        assert_eq!(output["results"].as_array().unwrap().len(), 257);
        assert_eq!(output["results"][256]["halfmoveClock"], 0);
        assert_eq!(
            output["results"][0]["identity"],
            output["results"][256]["identity"]
        );
        input["moves"].as_array_mut().unwrap().push(json!("a1b1"));
        assert!(dispatch("position.setupMoveSequence", &input).is_err());
    }

    #[test]
    fn setup_history_keeps_broad_initial_domain() {
        let input = json!({"queries":[{"placement":"7k/8/8/8/8/8/7R/7K","sideToMove":"white","castling":"-","enPassant":"-"}]});
        assert!(dispatch("position.setup", &input).is_ok());
        let fen = "7k/8/8/8/8/8/7R/7K w - - 0 1";
        assert!(advance(&sequence_position(fen, true).unwrap(), "h2g2").is_ok());
        assert!(sequence_position(fen, false).is_err());
    }
}
