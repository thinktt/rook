//! Diagnostic descriptor syntax and the explicit candidate component domain.
use super::{object, positions, text, Result};
use rook2::{
    position::Position,
    types::{Color, Move, MoveKind, PieceKind},
};
use serde_json::{json, Value};

pub(super) const PIECES: [&str; 6] = ["pawn", "knight", "bishop", "rook", "queen", "king"];
pub(super) const COLORS: [&str; 2] = ["white", "black"];

pub(super) fn piece(value: &Value) -> Result<PieceKind> {
    let name = text(value)?;
    PIECES
        .iter()
        .position(|&p| p == name)
        .map(|i| PieceKind::ALL[i])
        .ok_or_else(|| "invalid piece type".into())
}

pub(super) fn movement(value: &Value) -> Result<Option<Move>> {
    if value.is_null() {
        return Ok(None);
    }
    object(value, &["move", "kind"])?;
    let spelling = text(&value["move"])?;
    if !spelling.is_ascii() || !matches!(spelling.len(), 4 | 5) {
        return Err("invalid move spelling".into());
    }
    let from = positions::square(&json!(&spelling[..2]))?;
    let to = positions::square(&json!(&spelling[2..4]))?;
    if from == to {
        return Err("move endpoints must differ".into());
    }
    let kind = match text(&value["kind"])? {
        "ordinary" if spelling.len() == 4 => MoveKind::Ordinary,
        "ordinary" => MoveKind::Promotion(match spelling.as_bytes()[4] {
            b'n' => PieceKind::Knight,
            b'b' => PieceKind::Bishop,
            b'r' => PieceKind::Rook,
            b'q' => PieceKind::Queen,
            _ => return Err("invalid promotion choice".into()),
        }),
        "enPassant" if spelling.len() == 4 => MoveKind::EnPassant,
        "castle" if spelling.len() == 4 => MoveKind::Castle,
        _ => return Err("invalid move kind or suffix".into()),
    };
    Ok(Some(Move::new(from, to, kind)))
}

pub(super) fn descriptor(value: Move) -> Value {
    if value == Move::NONE {
        return Value::Null;
    }
    let kind = match value.kind() {
        MoveKind::EnPassant => "enPassant",
        MoveKind::Castle => "castle",
        _ => "ordinary",
    };
    json!({"move":value.to_string(),"kind":kind})
}

/// This is a supplied-candidate domain check, not complete chess legality.
pub(super) fn candidate(position: &Position, side: Color, movement: Move) -> Result<()> {
    let source = position.board[movement.from().0 as usize];
    let destination = position.board[movement.to().0 as usize];
    if source.is_empty()
        || source.color() != side
        || (!destination.is_empty()
            && (destination.color() == side || destination.kind() == PieceKind::King))
    {
        return Err("candidate source/destination outside component domain".into());
    }
    match movement.kind() {
        MoveKind::Ordinary => {}
        MoveKind::Promotion(_) if source.kind() == PieceKind::Pawn => {}
        MoveKind::EnPassant if source.kind() == PieceKind::Pawn && destination.is_empty() => {}
        MoveKind::Castle if source.kind() == PieceKind::King && destination.is_empty() => {}
        _ => return Err("candidate kind outside component domain".into()),
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn retained_descriptor_syntax_does_not_require_a_fitting_position() {
        assert!(movement(&json!({"move":"a2h7","kind":"castle"})).is_ok());
        assert!(movement(&json!({"move":"a2a3q","kind":"ordinary"})).is_ok());
        for invalid in [
            json!({"move":"a1a1","kind":"ordinary"}),
            json!({"move":"a2a3q","kind":"enPassant"}),
            json!({"move":"a2a3k","kind":"ordinary"}),
            json!({"move":"a2a3","kind":"ordinary","extra":0}),
        ] {
            assert!(movement(&invalid).is_err());
        }
    }
}
