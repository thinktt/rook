//! Noninteractive, explicitly partial development driver; not XBoard/DIAG-TRANSPORT.

use rook2::development::{self, Search, SEARCH_FIDELITY, SEARCH_OMISSIONS};
use rook2::evaluation::RootContext;
use rook2::influence::Influence;
use rook2::movegen::{generate_legal, MoveList};
use rook2::position::Position;
use rook2::types::{Color, Move, PieceKind};

const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

fn run() -> Result<(), String> {
    let mut args = std::env::args().skip(1);
    let mode = args.next().ok_or("usage: rook2-dev inspect|perft|search [--fen FEN] [--moves 'e2e4 ...'] [--depth N] [--repeat N]")?;
    let mut fen = START.to_owned();
    let mut root_fen = None;
    let mut moves = String::new();
    let mut depth = 4u8;
    let mut repeat = 1u32;
    let mut activity_weights = [1024i32; 2];
    let mut activity_material = None;
    while let Some(option) = args.next() {
        let value = args
            .next()
            .ok_or_else(|| format!("missing value for {option}"))?;
        match option.as_str() {
            "--fen" => fen = value,
            "--root-fen" => root_fen = Some(value),
            "--moves" => moves = value,
            "--depth" => depth = value.parse().map_err(|_| "invalid depth")?,
            "--repeat" => repeat = value.parse().map_err(|_| "invalid repeat")?,
            "--activity-weights" => {
                let parts: Vec<i32> = value
                    .split(',')
                    .map(str::parse)
                    .collect::<Result<_, _>>()
                    .map_err(|_| "invalid activity weights")?;
                if parts.len() != 2 || parts.iter().any(|v| !(0..=10240).contains(v)) {
                    return Err("activity weights require two integers 0..10240".into());
                }
                activity_weights = [parts[0], parts[1]];
            }
            "--activity-material" => {
                activity_material = Some(
                    value
                        .parse::<i32>()
                        .map_err(|_| "invalid activity material")?,
                )
            }
            _ => return Err(format!("unknown option {option}")),
        }
    }
    if depth > 8 || repeat == 0 || repeat > 100_000 {
        return Err("depth must be 0..8 and repeat 1..100000".into());
    }
    let mut position = Position::from_fen(&fen)?;
    for token in moves.split_ascii_whitespace() {
        let mut legal = MoveList::new();
        generate_legal(&position, &mut legal);
        let movement = legal
            .as_slice()
            .iter()
            .copied()
            .find(|m| m.to_string() == token)
            .ok_or_else(|| format!("illegal move {token}"))?;
        position = position.played_unchecked(movement);
    }
    position.validate()?;
    match mode.as_str() {
        "inspect" => {
            if repeat != 1 {
                return Err("inspect requires repeat=1".into());
            }
            let mut legal = MoveList::new();
            generate_legal(&position, &mut legal);
            let phase = position.phase();
            let root = match root_fen {
                Some(ref fen) => Position::from_fen(fen)?,
                None => position,
            };
            let context = RootContext::neutral(&root);
            let influence = Influence::build(&position);
            let activity = rook2::activity::compute(
                &position,
                &influence,
                activity_material.unwrap_or_else(|| context.material(&position)),
                activity_weights,
            );
            let side = if position.side == Color::White {
                "white"
            } else {
                "black"
            };
            let mut rights = String::new();
            for (bit, symbol) in [(2, 'K'), (1, 'Q'), (8, 'k'), (4, 'q')] {
                if position.rights & bit != 0 {
                    rights.push(symbol);
                }
            }
            if rights.is_empty() {
                rights.push('-');
            }
            let ep = if position.ep == 64 {
                "-".to_owned()
            } else {
                rook2::types::Square(position.ep).to_string()
            };
            println!(concat!("{{\"schema\":\"rook2-development-inspect-v1\",\"placement\":\"{}\",",
                "\"sideToMove\":\"{}\",\"castling\":\"{}\",\"enPassant\":\"{}\",\"halfmoveClock\":{},",
                "\"identity\":{{\"primary\":{},\"secondary\":{},\"pawn\":{},\"pawnGroup\":{}}},",
                "\"phase\":{{\"opening\":{},\"middlegame\":{},\"endgame\":{}}},",
                "\"pieceOrder\":{},\"legalMoves\":{},\"influenceCodes\":{:?},",
                "\"activity\":{{\"pieces\":{{\"white\":{},\"black\":{}}},\"activityPressure\":{{\"white\":{},\"black\":{}}},\"weightedActivity\":{},\"relationQueries\":{}}},",
                "\"material\":{},\"squareBalance\":{},\"positionBytes\":{},\"conformanceClaim\":false}}"),
                position.placement(), side, rights, ep, position.halfmove,
                position.primary, position.secondary, position.pawn, position.pawn % 128,
                phase.opening, phase.middlegame, phase.endgame,
                piece_order(&position), move_strings(legal.as_slice()), influence.profiles,
                activity.pieces[0], activity.pieces[1], activity.pressure[0], activity.pressure[1], activity.weighted, activity.relation_queries,
                context.material(&position), context.square_balance(&position), std::mem::size_of::<Position>());
        }
        "perft" => {
            let mut witness = 0u64;
            let mut last = 0;
            for _ in 0..repeat {
                last = development::perft(&position, depth);
                witness = witness.wrapping_add(last);
            }
            println!("{{\"schema\":\"rook2-development-perft-v1\",\"depth\":{depth},\"repeat\":{repeat},\"leaves\":{last},\"consumedLeaves\":{witness},\"conformanceClaim\":false}}");
        }
        "search" => {
            if depth == 0 {
                return Err("search requires depth 1..8".into());
            }
            let mut search = Search::new(&position);
            let mut last = None;
            let mut witness = 0u64;
            for _ in 0..repeat {
                let result = search.run(&position, depth);
                witness = witness
                    .wrapping_mul(0x100000001b3)
                    .wrapping_add(result.score as i64 as u64)
                    .wrapping_add(result.stats.nodes)
                    .wrapping_add(result.pv.first().map_or(0, |m| m.0 as u64));
                last = Some(result);
            }
            let result = last.unwrap();
            println!(concat!("{{\"schema\":\"rook2-development-search-v1\",\"fidelity\":\"{}\",",
                "\"omissions\":\"{}\",\"depth\":{},\"repeat\":{},\"score\":{},\"pv\":{},",
                "\"nodesPerSearch\":{},\"leafEvaluationsPerSearch\":{},\"generatedLegalMovesPerSearch\":{},",
                "\"searchedChildrenPerSearch\":{},\"cutoffsPerSearch\":{},\"influenceBuildsPerSearch\":{},\"activityEvaluationsPerSearch\":{},\"activityRelationQueriesPerSearch\":{},\"consumptionWitness\":{},",
                "\"semanticKingREWork\":null,\"conformanceClaim\":false}}"),
                SEARCH_FIDELITY, SEARCH_OMISSIONS, depth, repeat, result.score, move_strings(&result.pv),
                result.stats.nodes, result.stats.leaf_evaluations, result.stats.generated_legal_moves,
                result.stats.searched_children, result.stats.cutoffs, result.stats.influence_builds,
                result.stats.activity_evaluations, result.stats.activity_relation_queries, witness);
        }
        _ => return Err("mode must be inspect, perft or search".into()),
    }
    Ok(())
}

fn move_strings(moves: &[Move]) -> String {
    format!(
        "{:?}",
        moves.iter().map(ToString::to_string).collect::<Vec<_>>()
    )
}

fn piece_order(position: &Position) -> String {
    let mut colors = Vec::new();
    for color in [Color::White, Color::Black] {
        let mut kinds = Vec::new();
        for (kind, name) in PieceKind::ALL
            .into_iter()
            .zip(["pawn", "knight", "bishop", "rook", "queen", "king"])
        {
            let squares: Vec<String> = position
                .piece_squares(color, kind)
                .iter()
                .map(ToString::to_string)
                .collect();
            kinds.push(format!("\"{name}\":{squares:?}"));
        }
        let name = if color == Color::White {
            "white"
        } else {
            "black"
        };
        colors.push(format!("\"{name}\":{{{}}}", kinds.join(",")));
    }
    format!("{{{}}}", colors.join(","))
}

fn main() {
    if let Err(error) = run() {
        eprintln!("rook2-dev: {error}");
        std::process::exit(2);
    }
}
