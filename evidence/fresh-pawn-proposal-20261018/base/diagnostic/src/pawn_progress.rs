//! Ordered supplied-pawn/path schemas, backed by the native progress evaluator.
use super::{array, color, integer, object, positions, text, Result};
use rook2::{
    influence::Influence,
    pawn_progress::{self as native, Paths},
    position::Position,
    types::{Color, Piece, PieceKind, Square},
};
use serde_json::{json, Value};

fn candidates(position: &Position, value: &Value) -> Result<[Vec<Square>; 2]> {
    object(value, &["white", "black"])?;
    let mut result = [Vec::new(), Vec::new()];
    for (side, name) in [(Color::White, "white"), (Color::Black, "black")] {
        let mut seen = 0u64;
        for item in array(&value[name], 0, 8)? {
            let square = positions::square(item)?;
            if seen & (1u64 << square.0) != 0
                || position.board[square.0 as usize] != Piece::new(side, PieceKind::Pawn)
            {
                return Err("candidate list requires distinct present pawns of its color".into());
            }
            seen |= 1u64 << square.0;
            result[side.index()].push(square);
        }
    }
    Ok(result)
}

fn paths(value: &Value, side: Color) -> Result<Paths> {
    object(value, &["minimumPath", "bestPath", "bestTerminal"])?;
    let minimum = integer(&value["minimumPath"], 1, 100)?;
    let best = integer(&value["bestPath"], 1, 100)?;
    if (minimum > 12 && minimum != 100) || (best > 22 && best != 100) {
        return Err("path length outside diagnostic domain".into());
    }
    let terminal = if best == 100 {
        if !value["bestTerminal"].is_null() {
            return Err("absent best path requires null terminal".into());
        }
        None
    } else {
        let square = positions::square(&value["bestTerminal"])?;
        if square.rank() != if side == Color::White { 7 } else { 0 } {
            return Err("best terminal must lie on the selected color's promotion rank".into());
        }
        Some(square)
    };
    Ok(Paths {
        score: 0,
        minimum,
        best,
        terminal,
    })
}

fn path_output(paths: Paths) -> Value {
    json!({"score":paths.score,"minimumPath":paths.minimum,"bestPath":paths.best,
        "bestTerminal":paths.terminal.map(|square| square.to_string())})
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    object(input, &["queries"])?;
    let mut results = Vec::new();
    for query in array(&input["queries"], 1, 4096)? {
        let result = match operation {
            "evaluation.pawnProgress" => {
                object(query, &["placement", "pawnSquare"])?;
                let position = positions::placement(&query["placement"], true)?;
                let square = positions::square(&query["pawnSquare"])?;
                let piece = position.board[square.0 as usize];
                if piece.is_empty() || piece.kind() != PieceKind::Pawn {
                    return Err("pawnSquare must name a present pawn".into());
                }
                let influence = Influence::build(&position);
                json!({"score":native::raw(&position, &influence, square),"relationQueries":0})
            }
            "evaluation.pawnCandidates" | "evaluation.pawnCandidateEnding" => {
                object(query, &["placement", "sideToMove", "candidates"])?;
                let mut position = positions::placement(&query["placement"], true)?;
                position.side = color(&query["sideToMove"])?;
                let selected = candidates(&position, &query["candidates"])?;
                let influence = Influence::build(&position);
                let paths = [
                    native::candidates(&position, &influence, Color::White, &selected[0]),
                    native::candidates(&position, &influence, Color::Black, &selected[1]),
                ];
                if operation == "evaluation.pawnCandidates" {
                    json!({"white":path_output(paths[0]),"black":path_output(paths[1]),"relationQueries":0})
                } else {
                    let ending = native::ending(
                        &position,
                        &influence,
                        paths,
                        !selected[0].is_empty() || !selected[1].is_empty(),
                    );
                    json!({"whiteScore":paths[0].score,"blackScore":paths[1].score,"endingScore":ending,"relationQueries":0})
                }
            }
            "evaluation.pawnEnding" => {
                object(query, &["placement", "sideToMove", "kind", "paths"])?;
                let mut position = positions::placement(&query["placement"], true)?;
                position.side = color(&query["sideToMove"])?;
                object(&query["paths"], &["white", "black"])?;
                let paths = [
                    paths(&query["paths"]["white"], Color::White)?,
                    paths(&query["paths"]["black"], Color::Black)?,
                ];
                let ending = match text(&query["kind"])? {
                    "pawnOnly" => {
                        native::pawn_ending(&position, &Influence::build(&position), paths)
                    }
                    "queenPawn" => native::queen_ending(&position, paths),
                    _ => return Err("unknown pawn ending selection".into()),
                };
                json!({"endingScore":ending,"relationQueries":0})
            }
            _ => return Err(format!("unsupported pawn-progress operation: {operation}")),
        };
        results.push(result);
    }
    Ok(json!({"results":results}))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn supplied_candidate_order_survives_into_the_ending_tie() {
        // The released pawn-endings contract supplies this order-sensitive case.
        let query = json!({"placement":"8/P1P5/8/8/3K3k/8/p7/8","sideToMove":"white",
            "candidates":{"white":["a7","c7"],"black":["a2"]}});
        let first = dispatch(
            "evaluation.pawnCandidateEnding",
            &json!({"queries":[query.clone()]}),
        )
        .unwrap();
        let mut reversed = query;
        reversed["candidates"]["white"] = json!(["c7", "a7"]);
        let second = dispatch(
            "evaluation.pawnCandidateEnding",
            &json!({"queries":[reversed]}),
        )
        .unwrap();
        assert_eq!(first["results"][0]["endingScore"], 400);
        assert_eq!(second["results"][0]["endingScore"], 0);
        assert_eq!(
            first["results"][0]["whiteScore"],
            second["results"][0]["whiteScore"]
        );
    }

    #[test]
    fn candidate_membership_and_uniqueness_are_not_legal_selection_tests() {
        let query = json!({"placement":"7k/8/8/8/8/8/PN6/K7","sideToMove":"black",
            "candidates":{"white":["a2"],"black":[]}});
        assert!(dispatch(
            "evaluation.pawnCandidates",
            &json!({"queries":[query.clone()]})
        )
        .is_ok());
        let mut duplicate = query.clone();
        duplicate["candidates"]["white"] = json!(["a2", "a2"]);
        assert!(dispatch("evaluation.pawnCandidates", &json!({"queries":[duplicate]})).is_err());
        let mut wrong_piece = query;
        wrong_piece["candidates"]["white"] = json!(["b2"]);
        assert!(dispatch(
            "evaluation.pawnCandidates",
            &json!({"queries":[wrong_piece]})
        )
        .is_err());
        assert!(dispatch(
            "evaluation.pawnProgress",
            &json!({"queries":[{"placement":"7k/8/8/8/8/8/P7/K7","pawnSquare":"b2"}]})
        )
        .is_err());
    }

    #[test]
    fn supplied_path_measures_are_independent_but_terminal_domains_are_required() {
        let value = json!({"minimumPath":100,"bestPath":1,"bestTerminal":"h8"});
        assert!(paths(&value, Color::White).is_ok());
        let mut invalid = value.clone();
        invalid["minimumPath"] = json!(13);
        assert!(paths(&invalid, Color::White).is_err());
        invalid = value.clone();
        invalid["bestTerminal"] = json!("h7");
        assert!(paths(&invalid, Color::White).is_err());
        invalid = value;
        invalid["bestPath"] = json!(100);
        assert!(paths(&invalid, Color::White).is_err());
        invalid["bestTerminal"] = Value::Null;
        assert!(paths(&invalid, Color::White).is_ok());
    }
}
