//! Noninteractive, explicitly partial development driver; not XBoard/DIAG-TRANSPORT.

use rook2::development::{self, Search, SEARCH_FIDELITY, SEARCH_OMISSIONS};
use rook2::evaluation::RootContext;
use rook2::history::SearchHistory;
use rook2::influence::Influence;
use rook2::movegen::{generate_legal, MoveList};
use rook2::pawn_structure::{PawnStructure, Weakness};
use rook2::position::Position;
use rook2::types::{Color, Move, PieceKind};

const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

fn run() -> Result<(), String> {
    let mut args = std::env::args().skip(1);
    let mode = args.next().ok_or("usage: rook2-dev inspect|perft|search|quiescence|first-iteration|ordinary [--fen FEN] [--moves 'e2e4 ...'] [--root-move MOVE] [--depth N] [--repeat N]")?;
    let mut fen = START.to_owned();
    let mut root_fen = None;
    let mut moves = String::new();
    let mut depth = 4u8;
    let mut repeat = 1u32;
    let mut root_move = None;
    let mut iteration_depth = 1i32;
    let mut max_nodes = 4095u64;
    let mut diagnostics = true;
    let mut tts_bytes = 67_108_864usize;
    let mut activity_weights = [1024i32; 2];
    let mut activity_material = None;
    let mut position_weights = [1024i32; 2];
    let mut shelter_pressure = None;
    let mut pawn_doubled = [1024i32; 2];
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
            "--root-move" => root_move = Some(value),
            "--tts-bytes" => tts_bytes = value.parse().map_err(|_| "invalid TT capacity")?,
            "--iteration-depth" => {
                iteration_depth = value.parse().map_err(|_| "invalid iteration depth")?
            }
            "--max-nodes" => max_nodes = value.parse().map_err(|_| "invalid node limit")?,
            "--diagnostics" => {
                diagnostics = match value.as_str() {
                    "on" => true,
                    "off" => false,
                    _ => return Err("diagnostics must be on or off".into()),
                }
            }
            "--activity-weights" => {
                activity_weights = bounded_pair(&value, 0, 4096, "activity weights")?;
            }
            "--activity-material" => {
                let material = value
                    .parse::<i32>()
                    .map_err(|_| "invalid activity material")?;
                if !(-100_000..=100_000).contains(&material) {
                    return Err("activity material requires an integer -100000..100000".into());
                }
                activity_material = Some(material);
            }
            "--position-weights" => {
                position_weights = bounded_pair(&value, 0, 4096, "position weights")?
            }
            "--shelter-pressure" => {
                shelter_pressure = Some(bounded_pair(&value, 0, 4096, "shelter pressure")?)
            }
            "--pawn-doubled" => {
                pawn_doubled = bounded_pair(&value, -10_000, 10_000, "pawn doubled coefficients")?
            }
            _ => return Err(format!("unknown option {option}")),
        }
    }
    if depth > 8 || repeat == 0 || repeat > 100_000 {
        return Err("depth must be 0..8 and repeat 1..100000".into());
    }
    if !(1..=99).contains(&iteration_depth) || !(1..=100_000_000).contains(&max_nodes) {
        return Err("iteration depth must be 1..99 and max nodes 1..100000000".into());
    }
    if !(96..=1_073_741_824).contains(&tts_bytes) {
        return Err("TT capacity must be 96..1073741824 bytes".into());
    }
    let mut position = Position::from_fen(&fen)?;
    if matches!(mode.as_str(), "quiescence" | "first-iteration" | "ordinary")
        && rook2::movegen::in_check(&position, position.side.opponent())
    {
        return Err("search setup's side not to move is already in check".into());
    }
    let mut history = SearchHistory::new(&position);
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
        history.push(&position, Some(movement));
    }
    history.mark_root();
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
            let material = activity_material.unwrap_or_else(|| context.material(&position));
            let activity =
                rook2::activity::compute(&position, &influence, material, activity_weights);
            let position_terms = rook2::shelter::compute(
                &position,
                &influence,
                activity.pressure,
                material,
                position_weights,
            );
            let shelter = match shelter_pressure {
                Some(pressure) => rook2::shelter::compute(
                    &position,
                    &influence,
                    pressure,
                    material,
                    position_weights,
                ),
                None => position_terms,
            };
            let pawn_structure = rook2::pawn_structure::fresh(&position, &influence, pawn_doubled);
            let structure_terms =
                rook2::pawn_terms::structure_terms(&position, &influence, &pawn_structure);
            let raw_piece_terms =
                rook2::pawn_terms::raw_piece_terms(&position, &influence, &pawn_structure);
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
                "\"activity\":{{\"pieces\":{{\"white\":{},\"black\":{}}},\"activityPressure\":{{\"white\":{},\"black\":{}}},\"weightedActivity\":{},\"positionTerms\":{{\"white\":{},\"black\":{},\"weighted\":{}}},\"relationQueries\":{}}},",
                "\"kingShelter\":{{\"white\":{{\"term\":{}}},\"black\":{{\"term\":{}}},\"weighted\":{}}},",
                "\"pawnStructure\":{},\"pawnStructureScore\":{},",
                "\"pawnPiece\":{{\"white\":{},\"black\":{},\"relationQueries\":{}}},",
                "\"material\":{},\"squareBalance\":{},\"positionBytes\":{},\"conformanceClaim\":false}}"),
                position.placement(), side, rights, ep, position.halfmove,
                position.primary, position.secondary, position.pawn, position.pawn % 128,
                phase.opening, phase.middlegame, phase.endgame,
                piece_order(&position), move_strings(legal.as_slice()), influence.profiles,
                activity.pieces[0], activity.pieces[1], activity.pressure[0], activity.pressure[1], activity.weighted,
                position_terms.terms[0], position_terms.terms[1], position_terms.weighted, activity.relation_queries,
                shelter.terms[0], shelter.terms[1], shelter.weighted,
                pawn_structure_json(&pawn_structure, None), pawn_structure_json(&pawn_structure, Some(structure_terms)),
                raw_piece_terms.0[0], raw_piece_terms.0[1], raw_piece_terms.1,
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
        "quiescence" => {
            let token = root_move.ok_or("quiescence requires --root-move")?;
            let mut legal = MoveList::new();
            generate_legal(&position, &mut legal);
            let movement = legal
                .as_slice()
                .iter()
                .copied()
                .find(|m| m.to_string() == token)
                .ok_or_else(|| format!("illegal root move {token}"))?;
            if diagnostics {
                run_quiescence::<true>(
                    position,
                    &mut history,
                    movement,
                    repeat,
                    iteration_depth,
                    max_nodes,
                )?;
            } else {
                run_quiescence::<false>(
                    position,
                    &mut history,
                    movement,
                    repeat,
                    iteration_depth,
                    max_nodes,
                )?;
            }
        }
        "first-iteration" => {
            if iteration_depth != 1 || root_move.is_some() {
                return Err(
                    "first-iteration requires iteration depth 1 and no root move selection".into(),
                );
            }
            if diagnostics {
                run_first_iteration::<true>(position, &mut history, repeat, max_nodes)?;
            } else {
                run_first_iteration::<false>(position, &mut history, repeat, max_nodes)?;
            }
        }
        "ordinary" => {
            if depth == 0 || root_move.is_some() {
                return Err("ordinary requires depth 1..8 and no selected root move".into());
            }
            if diagnostics {
                run_ordinary::<true>(position, &mut history, depth, repeat, max_nodes, tts_bytes)?;
            } else {
                run_ordinary::<false>(position, &mut history, depth, repeat, max_nodes, tts_bytes)?;
            }
        }
        _ => {
            return Err(
                "mode must be inspect, perft, search, quiescence, first-iteration or ordinary"
                    .into(),
            )
        }
    }
    Ok(())
}

fn step_json(s: &rook2::first_iteration::Step) -> String {
    format!(concat!("{{\"move\":\"{}\",\"window\":[{},10000],\"score\":{},\"bestScore\":{},\"secondScore\":{},",
        "\"childPv\":{},\"pv\":{},\"nodes\":{},\"relationQueries\":{}}}"),
        s.movement, s.lower, s.score, s.best, s.second, move_strings(&s.child_pv),
        move_strings(&s.root_pv), s.work.charged_search_units, s.work.charged_relation_queries)
}

fn run_ordinary<const D: bool>(
    position: Position,
    history: &mut SearchHistory,
    depth: u8,
    repeat: u32,
    max_nodes: u64,
    tts_bytes: usize,
) -> Result<(), String> {
    use rook2::engine::Search;
    use rook2::ordinary::{Outcome, FIDELITY};
    use rook2::quiescence::Limits;
    let mut engine = Search::<D>::new(&position);
    engine.config.tts_bytes = tts_bytes;
    let mut last: Option<Outcome> = None;
    let mut witness = 0u64;
    for _ in 0..repeat {
        let out = engine
            .run_iterations(
                position,
                history,
                depth,
                Limits {
                    nodes: Some(max_nodes),
                },
            )
            .map_err(|e| format!("ordinary iterations incomplete: {e:?}"))?;
        if let Some(previous) = &last {
            if (previous.score, &previous.pv, previous.work) != (out.score, &out.pv, out.work)
                || previous
                    .iterations
                    .iter()
                    .zip(&out.iterations)
                    .any(|(a, b)| {
                        (a.score, &a.pv, &a.candidates, &a.steps, a.work)
                            != (b.score, &b.pv, &b.candidates, &b.steps, b.work)
                    })
            {
                return Err(
                    "fresh repeated ordinary search changed its result, ranking or work".into(),
                );
            }
        }
        witness = witness
            .wrapping_mul(0x100000001b3)
            .wrapping_add(out.score as i64 as u64)
            .wrapping_add(out.work.charged_search_units)
            .wrapping_add(out.work.charged_relation_queries);
        last = Some(out);
    }
    let out = last.unwrap();
    let iterations: Vec<String> = out
        .iterations
        .iter()
        .map(|i| {
            let steps: Vec<String> = i.steps.iter().map(step_json).collect();
            format!(
                concat!(
                    "{{\"depth\":{},\"candidates\":{},\"steps\":[{}],\"score\":{},\"pv\":{},",
                    "\"nodes\":{},\"relationQueries\":{}}}"
                ),
                i.depth,
                move_strings(&i.candidates),
                steps.join(","),
                i.score,
                move_strings(&i.pv),
                i.work.charged_search_units,
                i.work.charged_relation_queries
            )
        })
        .collect();
    let s = out.stats;
    let e = out.evaluations;
    let counts = if D {
        format!(concat!("{{\"ordinaryNodes\":{},\"tableProbes\":{},\"tableHits\":{},\"tableStores\":{},",
        "\"full\":{},\"fast\":{},\"influenceBuilds\":{},\"pawnReuses\":{},\"pawnReplacements\":{},",
        "\"fastCutoffs\":{},\"shallowCutoffs\":{},\"nullTrials\":{},\"mateProbes\":{},",
        "\"iioPasses\":{},\"iioChildren\":{},\"scoutRetries\":{},\"frontierSkips\":{},\"materialThreats\":{},",
        "\"iioInitialPhases\":{},\"iioTailPhases\":{},\"accumulatedExtensionUses\":{},\"refreshedScoutRetries\":{}}}"),
        s.ordinary_nodes, s.table_probes, s.table_hits, s.table_stores, e.full, e.fast, e.influence_builds,
        e.pawn_reuses, e.pawn_replacements, s.fast_cutoffs, s.shallow_cutoffs, s.null_trials,
        s.mate_probes, s.iio_passes, s.iio_children, s.scout_retries, s.frontier_skips, s.material_threats,
        s.iio_initial_phases, s.iio_tail_phases, s.accumulated_extension_uses, s.refreshed_scout_retries)
    } else {
        "null".to_owned()
    };
    println!(concat!("{{\"schema\":\"rook2-development-ordinary-iterations-v1\",\"fidelity\":\"{}\",",
        "\"omissions\":\"{}; timed/work-clock root scheduling; host polling; personality/protocol integration\",",
        "\"diagnostics\":{},\"depth\":{},\"repeat\":{},\"ttsBytes\":{},\"score\":{},\"pv\":{},",
        "\"initialCandidates\":{},\"iterations\":[{}],\"nodesPerSearch\":{},\"chargedRelationQueriesPerSearch\":{},",
        "\"diagnosticCounts\":{},\"consumptionWitness\":{},\"conformanceClaim\":false}}"),
        FIDELITY, rook2::evaluator::OMITTED_TERMS, D, depth, repeat, tts_bytes, out.score,
        move_strings(&out.pv), move_strings(&out.initial_candidates), iterations.join(","),
        out.work.charged_search_units, out.work.charged_relation_queries, counts, witness);
    Ok(())
}

fn run_first_iteration<const DIAGNOSTICS: bool>(
    position: Position,
    history: &mut SearchHistory,
    repeat: u32,
    max_nodes: u64,
) -> Result<(), String> {
    use rook2::first_iteration::{self, Outcome, FIDELITY};
    use rook2::quiescence::{Limits, Quiescence};
    let mut search = Quiescence::<DIAGNOSTICS>::new(&position);
    let mut last: Option<Outcome> = None;
    let mut witness = 0u64;
    for _ in 0..repeat {
        let result = first_iteration::run(
            &mut search,
            position,
            history,
            Limits {
                nodes: Some(max_nodes),
            },
        )
        .map_err(|e| format!("first iteration incomplete: {e:?}"))?;
        if let Some(previous) = &last {
            if (previous.score, &previous.pv, previous.work, &previous.steps)
                != (result.score, &result.pv, result.work, &result.steps)
            {
                return Err(
                    "fresh repeated root iteration changed its result, steps or work".into(),
                );
            }
        }
        witness = witness
            .wrapping_mul(0x100000001b3)
            .wrapping_add(result.score as i64 as u64)
            .wrapping_add(result.work.charged_search_units)
            .wrapping_add(result.work.charged_relation_queries);
        last = Some(result);
    }
    let out = last.unwrap();
    let steps: Vec<String> = out
        .steps
        .iter()
        .map(|s| {
            format!(
                concat!(
        "{{\"move\":\"{}\",\"window\":[{},10000],\"score\":{},\"bestScore\":{},\"secondScore\":{},",
        "\"childPv\":{},\"pv\":{},\"nodes\":{},\"relationQueries\":{}}}"),
                s.movement,
                s.lower,
                s.score,
                s.best,
                s.second,
                move_strings(&s.child_pv),
                move_strings(&s.root_pv),
                s.work.charged_search_units,
                s.work.charged_relation_queries
            )
        })
        .collect();
    let e = out.evaluations;
    println!(concat!("{{\"schema\":\"rook2-development-first-iteration-v1\",\"fidelity\":\"{}\",",
        "\"omissions\":\"{}; later ordinary iterations/TT; host polling/timing; production protocol\",",
        "\"diagnostics\":{},\"repeat\":{},\"score\":{},\"pv\":{},\"candidates\":{},\"steps\":[{}],",
        "\"nodesPerSearch\":{},\"chargedRelationQueriesPerSearch\":{},\"fullEvaluationsPerSearch\":{},",
        "\"fastEvaluationsPerSearch\":{},\"influenceBuildsPerSearch\":{},",
        "\"pawnReusesPerSearch\":{},\"pawnReplacementsPerSearch\":{},",
        "\"consumptionWitness\":{},\"conformanceClaim\":false}}"),
        FIDELITY, rook2::evaluator::OMITTED_TERMS, DIAGNOSTICS, repeat, out.score,
        move_strings(&out.pv), move_strings(&out.candidates), steps.join(","),
        out.work.charged_search_units, out.work.charged_relation_queries, e.full, e.fast,
        e.influence_builds, e.pawn_reuses, e.pawn_replacements, witness);
    Ok(())
}

fn run_quiescence<const DIAGNOSTICS: bool>(
    position: Position,
    history: &mut SearchHistory,
    movement: Move,
    repeat: u32,
    iteration_depth: i32,
    max_nodes: u64,
) -> Result<(), String> {
    use rook2::quiescence::{Entry, Limits, Quiescence, FIDELITY};
    let mut search = Quiescence::<DIAGNOSTICS>::new(&position);
    let mut last: Option<rook2::quiescence::Outcome> = None;
    let mut witness = 0u64;
    for _ in 0..repeat {
        let root = search.prepare_root(position);
        let mut child = root.child(&search.evaluator.root, movement);
        history.reset_search();
        history.push(&child.position, Some(movement));
        let result = search.search_subtree(
            &mut child,
            history,
            Entry {
                ply: 1,
                target: 1,
                iteration_depth,
                lower: -10000,
                upper: 10000,
                analysis: 0,
                capture_exception: rook2::quiescence_policy::capture_exception(
                    &position, &movement,
                ),
            },
            Limits {
                nodes: Some(max_nodes),
            },
        );
        history.pop();
        let result = result.map_err(|stop| format!("quiescence incomplete: {stop:?}"))?;
        if let Some(previous) = &last {
            if (previous.score, &previous.pv, previous.work)
                != (result.score, &result.pv, result.work)
            {
                return Err("fresh repeated quiescence changed its result or work".into());
            }
        }
        witness = witness
            .wrapping_mul(0x100000001b3)
            .wrapping_add(result.score as i64 as u64)
            .wrapping_add(result.work.charged_search_units)
            .wrapping_add(result.work.charged_relation_queries);
        last = Some(result);
    }
    let out = last.unwrap();
    let s = out.stats;
    let e = out.evaluations;
    println!(concat!("{{\"schema\":\"rook2-development-quiescence-v1\",\"fidelity\":\"{}\",",
        "\"omissions\":\"{}; host polling/timed stopping; ordinary search and protocol\",",
        "\"diagnostics\":{},\"iterationDepth\":{},\"repeat\":{},\"rootMove\":\"{}\",\"score\":{},\"pv\":{},",
        "\"nodesPerSearch\":{},\"chargedRelationQueriesPerSearch\":{},",
        "\"generatedPerSearch\":{},\"examinedPerSearch\":{},\"childrenPerSearch\":{},",
        "\"projectionsPerSearch\":{},\"replyProbesPerSearch\":{},\"reusedReplyListsPerSearch\":{},",
        "\"optimisticUpdatesPerSearch\":{},\"unsafeRejectionsPerSearch\":{},\"cutoffsPerSearch\":{},",
        "\"fullEvaluationsPerSearch\":{},\"fastEvaluationsPerSearch\":{},\"influenceBuildsPerSearch\":{},",
        "\"pawnReusesPerSearch\":{},\"pawnReplacementsPerSearch\":{},\"lateEndgameEvaluationsPerSearch\":{},",
        "\"consumptionWitness\":{},\"conformanceClaim\":false}}"),
        FIDELITY, rook2::evaluator::OMITTED_TERMS, DIAGNOSTICS, iteration_depth, repeat, movement,
        out.score, move_strings(&out.pv), out.work.charged_search_units, out.work.charged_relation_queries,
        s.generated, s.examined, s.children, s.projections, s.reply_probes, s.reused_reply_lists,
        s.optimistic_updates, s.unsafe_rejections, s.cutoffs, e.full, e.fast, e.influence_builds,
        e.pawn_reuses, e.pawn_replacements, s.late_endgame_evaluations, witness);
    Ok(())
}

fn bounded_pair(value: &str, low: i32, high: i32, name: &str) -> Result<[i32; 2], String> {
    let parts: Vec<i32> = value
        .split(',')
        .map(str::parse)
        .collect::<Result<_, _>>()
        .map_err(|_| format!("invalid {name}"))?;
    if parts.len() != 2 || parts.iter().any(|v| !(low..=high).contains(v)) {
        return Err(format!("{name} require two integers {low}..{high}"));
    }
    Ok([parts[0], parts[1]])
}

fn pawn_structure_json(structure: &PawnStructure, score: Option<([i32; 2], u64)>) -> String {
    let mut colors = Vec::new();
    for (side, name) in [(Color::White, "white"), (Color::Black, "black")] {
        // Canonical cold output only: never mutate semantic/cache chronology.
        let mut pawns = structure.pawn_slice(side).to_vec();
        pawns.sort_by_key(|pawn| (pawn.square.file(), pawn.square.rank()));
        let observations: Vec<String> = pawns
            .iter()
            .map(|pawn| {
                let weakness = match pawn.weakness {
                    Weakness::None => "none",
                    Weakness::Isolated => "isolated",
                    Weakness::BlockedBackward => "blocked-backward",
                    Weakness::ExposedBackward => "exposed-backward",
                    Weakness::ExposedLevel => "exposed-level",
                };
                format!(
                    "{{\"square\":\"{}\",\"candidate\":{},\"weakness\":\"{weakness}\"}}",
                    pawn.square, pawn.candidate
                )
            })
            .collect();
        let extra = if let Some((scores, _)) = score {
            let candidates: Vec<String> = pawns
                .iter()
                .filter(|pawn| pawn.candidate)
                .map(|pawn| pawn.square.to_string())
                .collect();
            format!(
                ",\"structureScore\":{},\"candidates\":{candidates:?}",
                scores[side.index()]
            )
        } else {
            String::new()
        };
        colors.push(format!(
            "\"{name}\":{{\"baseScore\":{},\"pawns\":[{}]{extra}}}",
            structure.base_score[side.index()],
            observations.join(",")
        ));
    }
    let work = score
        .map(|(_, queries)| format!(",\"relationQueries\":{queries}"))
        .unwrap_or_default();
    format!("{{{}{work}}}", colors.join(","))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn cold_parameter_bounds_accept_signed_doubled_and_reject_invalid_pairs() {
        assert_eq!(
            bounded_pair("-10000,10000", -10000, 10000, "doubled").unwrap(),
            [-10000, 10000]
        );
        for invalid in ["-1,0", "0,4097", "0", "0,1,2", "x,0"] {
            assert!(bounded_pair(invalid, 0, 4096, "weight").is_err());
        }
    }

    #[test]
    fn canonical_fresh_output_does_not_reorder_native_descriptors() {
        let position = Position::from_fen("7k/8/8/2P5/3P4/2P5/8/K7 w - - 0 1").unwrap();
        let structure =
            rook2::pawn_structure::fresh(&position, &Influence::build(&position), [1024; 2]);
        let before = structure;
        let json = pawn_structure_json(&structure, None);
        let c3 = json.find("\"square\":\"c3\"").unwrap();
        let c5 = json.find("\"square\":\"c5\"").unwrap();
        let d4 = json.find("\"square\":\"d4\"").unwrap();
        assert!(c3 < c5 && c5 < d4);
        assert_eq!(structure, before);
    }
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
