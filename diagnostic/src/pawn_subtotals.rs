//! Cold fresh/retained pawn composition. Native owners produce context, scores and work.
use super::{array, boolean, color, integer, object, pawn_progress, phase, positions, scores, Result};
use rook2::{
    evaluation::RootContext,
    evaluator,
    influence::Influence,
    pawn_progress as native, pawn_structure,
    pawn_terms::{self, PawnTerms},
    position::{Phase, Position},
    positional_terms,
    types::{Color, PieceKind, Square},
};
use serde_json::{json, Value};

const COLORS: [&str; 2] = ["white", "black"];

#[derive(Clone, Copy)]
struct Weights {
    structure: [i32; 2],
    progress: [i32; 2],
}

impl Weights {
    fn parse(value: &Value) -> Result<Self> {
        object(value, &COLORS)?;
        let mut structure = [0; 2];
        let mut progress = [0; 2];
        for (index, name) in COLORS.iter().enumerate() {
            object(&value[*name], &["structure", "progress"])?;
            structure[index] = integer(&value[*name]["structure"], -10_000, 10_000)?;
            progress[index] = integer(&value[*name]["progress"], -10_000, 10_000)?;
        }
        Ok(Self {
            structure,
            progress,
        })
    }
}

fn pawn_order(position: &Position, value: &Value) -> Result<[Vec<Square>; 2]> {
    // Candidate-list validation checks every item for color, membership and
    // uniqueness. Equal counts then establish a complete pawn enumeration.
    let order = pawn_progress::candidates(position, value)?;
    for side in [Color::White, Color::Black] {
        if order[side.index()].len()
            != position.counts[side.index()][PieceKind::Pawn.index()] as usize
        {
            return Err("pawn order must contain every current pawn exactly once".into());
        }
    }
    Ok(order)
}

enum Candidates {
    Supplied { scores: [i32; 2], ending: i32 },
    Produced([Vec<Square>; 2]),
}

struct Subtotal {
    position: Position,
    phase: Phase,
    material: i32,
    weights: Weights,
    terms: PawnTerms,
    candidates: Candidates,
}

impl Subtotal {
    fn parse(query: &Value, produced: bool) -> Result<Self> {
        let mut fields = vec!["placement", "phase", "materialScore", "weights", "terms"];
        if produced {
            fields.extend(["sideToMove", "candidates"]);
        } else {
            fields.push("endingScore");
        }
        object(query, &fields)?;
        let mut position = positions::placement(&query["placement"], true)?;
        let phase = phase(&query["phase"])?;
        let material = integer(&query["materialScore"], -10_000, 10_000)?;
        let weights = Weights::parse(&query["weights"])?;
        object(&query["terms"], &COLORS)?;
        let mut terms = PawnTerms::default();
        let mut candidate_scores = [0; 2];
        for (index, name) in COLORS.iter().enumerate() {
            let term = &query["terms"][*name];
            if produced {
                object(term, &["structureScore", "pieceTerm"])?;
            } else {
                object(term, &["structureScore", "pieceTerm", "candidateScore"])?;
                candidate_scores[index] = integer(&term["candidateScore"], 0, 4096)?;
            }
            terms.structure[index] = integer(&term["structureScore"], -4096, 4096)?;
            terms.piece[index] = integer(&term["pieceTerm"], 0, 4096)?;
        }
        let candidates = if produced {
            position.side = color(&query["sideToMove"])?;
            Candidates::Produced(pawn_progress::candidates(&position, &query["candidates"])?)
        } else {
            Candidates::Supplied {
                scores: candidate_scores,
                ending: integer(&query["endingScore"], -10_000, 10_000)?,
            }
        };
        Ok(Self {
            position,
            phase,
            material,
            weights,
            terms,
            candidates,
        })
    }

    fn observe(self) -> Value {
        let (scores, ending) = match self.candidates {
            Candidates::Supplied { scores, ending } => (scores, ending),
            Candidates::Produced(candidates) => {
                let influence = Influence::build(&self.position);
                let paths = [
                    native::candidates(&self.position, &influence, Color::White, &candidates[0]),
                    native::candidates(&self.position, &influence, Color::Black, &candidates[1]),
                ];
                let ending = native::ending(
                    &self.position,
                    &influence,
                    paths,
                    !candidates[0].is_empty() || !candidates[1].is_empty(),
                );
                ([paths[0].score, paths[1].score], ending)
            }
        };
        let ending = native::fallback(&self.position, ending);
        subtotal_output(
            self.phase,
            self.weights,
            &self.terms,
            scores,
            ending,
            native::weighted(
                self.phase,
                self.material,
                self.weights.progress,
                scores,
                ending,
            ),
        )
    }
}

struct Fresh {
    position: Position,
    phase: Phase,
    material: i32,
    weights: Weights,
    order: [Vec<Square>; 2],
}

impl Fresh {
    fn parse(query: &Value) -> Result<Self> {
        object(
            query,
            &[
                "placement",
                "sideToMove",
                "phase",
                "materialScore",
                "weights",
                "pawnOrder",
            ],
        )?;
        Self::parse_fields(query)
    }

    // The caller owns the exact object schema; all supplied fields are parsed.
    fn parse_fields(query: &Value) -> Result<Self> {
        let mut position = positions::placement(&query["placement"], true)?;
        position.side = color(&query["sideToMove"])?;
        let phase = phase(&query["phase"])?;
        let material = integer(&query["materialScore"], -10_000, 10_000)?;
        let weights = Weights::parse(&query["weights"])?;
        let order = pawn_order(&position, &query["pawnOrder"])?;
        Ok(Self {
            position,
            phase,
            material,
            weights,
            order,
        })
    }

    fn observe(self) -> Value {
        let influence = Influence::build(&self.position);
        fresh_output(
            &self.position,
            &influence,
            self.phase,
            self.material,
            self.weights,
            &self.order,
        )
    }
}

struct Context {
    root: Position,
    current: Position,
    percentages: [[u16; 11]; 2],
    average_depth: i32,
    order: [Vec<Square>; 2],
}

impl Context {
    fn parse(query: &Value) -> Result<Self> {
        object(
            query,
            &[
                "rootPlacement",
                "placement",
                "rootSide",
                "sideToMove",
                "percentages",
                "averageDepth",
                "pawnOrder",
            ],
        )?;
        let mut root = positions::placement(&query["rootPlacement"], true)?;
        root.side = color(&query["rootSide"])?;
        let mut current = positions::placement(&query["placement"], true)?;
        current.side = color(&query["sideToMove"])?;
        let average_depth = integer(&query["averageDepth"], -100, 100)?;
        let order = pawn_order(&current, &query["pawnOrder"])?;
        let percentages = percentages(&query["percentages"], root.side)?;
        Ok(Self {
            root,
            current,
            percentages,
            average_depth,
            order,
        })
    }

    fn observe(self) -> Value {
        let context = ContextBinding::new(&self.root, self.percentages, self.average_depth);
        let influence = Influence::build(&self.current);
        let structure = pawn_structure::fresh_with_order(
            &self.current, &influence, [&self.order[0], &self.order[1]], [1024; 2],
        );
        context.observe(&self.current, &influence, &structure)
    }
}

/// Complete percentages are parsed even when a contribution ignores one.
fn percentages(value: &Value, root_side: Color) -> Result<[[u16; 11]; 2]> {
    object(value, &["own", "opponent"])?;
    let mut result = [[0; 11]; 2];
    for (owner, side) in [("own", root_side), ("opponent", root_side.opponent())] {
        object(&value[owner], &scores::NAMES)?;
        for (index, name) in scores::NAMES.iter().enumerate() {
            result[side.index()][index] = integer(&value[owner][*name], 0, 1000)? as u16;
        }
    }
    Ok(result)
}

/// Cold binding shared with fresh context. Native root material and coefficient
/// owners retain all formulas; this record only carries their produced values.
struct ContextBinding {
    root: RootContext,
    weights: Weights,
    central: [i32; 2],
}

impl ContextBinding {
    fn new(position: &Position, percentages: [[u16; 11]; 2], average_depth: i32) -> Self {
        let material_percentages = [
            std::array::from_fn(|index| percentages[0][index]),
            std::array::from_fn(|index| percentages[1][index]),
        ];
        let root = RootContext::new(position, material_percentages, average_depth);
        let pair = |index| {
            [
                evaluator::coefficient(percentages[0][index] as i32),
                evaluator::coefficient(percentages[1][index] as i32),
            ]
        };
        // Produced 10240 is valid here; never reparse through supplied weights.
        Self {
            root,
            weights: Weights { structure: pair(10), progress: pair(9) },
            central: pair(6),
        }
    }

    fn observe(&self, position: &Position, influence: &Influence, structure: &pawn_structure::PawnStructure) -> Value {
        let phase = position.phase();
        let material = self.root.material(position);
        let pawn = selected_output(position, influence, phase, material, self.weights, structure);
        let central = positional_terms::central(influence, phase, self.central);
        json!({"rootPhase":positions::phase_value(self.root.phase),
            "currentPhase":positions::phase_value(phase),"materialScore":material,"pawn":pawn,
            "central":{"white":central.colors[0],"black":central.colors[1],"weighted":central.weighted}})
    }
}

struct RetainedStep {
    supplied: Fresh,
    clear: bool,
}

impl RetainedStep {
    fn parse(input: &Value) -> Result<Vec<Self>> {
        object(input, &["steps"])?;
        array(&input["steps"], 1, 4096)?.iter().map(|step| {
            object(step, &["placement", "sideToMove", "phase", "materialScore", "weights", "pawnOrder", "clear"])?;
            Ok(Self { supplied: Fresh::parse_fields(step)?, clear: boolean(&step["clear"])? })
        }).collect()
    }
}

fn retained_subtotals(input: &Value) -> Result<Value> {
    // Parse the entire request before influence, cache construction or selection.
    let steps = RetainedStep::parse(input)?;
    let mut cache = pawn_structure::PawnCache::new();
    let mut results = Vec::with_capacity(steps.len());
    for step in steps {
        if step.clear { cache.clear(); }
        let q = step.supplied;
        let influence = Influence::build(&q.position);
        let selected = cache.select_with_order(&q.position, &influence, [&q.order[0], &q.order[1]]);
        let pawn = selected_output(&q.position, &influence, q.phase, q.material, q.weights, &selected.structure);
        results.push(json!({"identity":positions::identity(&q.position),"reused":selected.reused,"pawn":pawn}));
    }
    Ok(json!({"results":results}))
}

struct OrderedPosition {
    position: Position,
    order: [Vec<Square>; 2],
}

impl OrderedPosition {
    fn parse(value: &Value) -> Result<Self> {
        object(value, &["placement", "sideToMove", "pawnOrder"])?;
        let mut position = positions::placement(&value["placement"], true)?;
        position.side = color(&value["sideToMove"])?;
        let order = pawn_order(&position, &value["pawnOrder"])?;
        Ok(Self { position, order })
    }
}

struct SearchSequence {
    positions: Vec<OrderedPosition>,
    percentages: [[u16; 11]; 2],
    average_depth: i32,
}

impl SearchSequence {
    fn parse(input: &Value) -> Result<Self> {
        object(input, &["rootSide", "averageDepth", "percentages", "positions"])?;
        let root_side = color(&input["rootSide"])?;
        let average_depth = integer(&input["averageDepth"], -100, 100)?;
        let percentages = percentages(&input["percentages"], root_side)?;
        let positions = array(&input["positions"], 1, 4096)?.iter()
            .map(OrderedPosition::parse).collect::<Result<Vec<_>>>()?;
        if positions[0].position.side != root_side {
            return Err("first position sideToMove must equal rootSide".into());
        }
        Ok(Self { positions, percentages, average_depth })
    }

    fn observe(self) -> Value {
        // Both owners are request-local and constructed only after full parsing.
        // Root phase/counts/ownership bind once; current phase/material do not.
        let context = ContextBinding::new(&self.positions[0].position, self.percentages, self.average_depth);
        let mut cache = pawn_structure::PawnCache::new();
        let mut results = Vec::with_capacity(self.positions.len());
        for current in self.positions {
            let influence = Influence::build(&current.position);
            let selected = cache.select_with_order(&current.position, &influence, [&current.order[0], &current.order[1]]);
            let mut result = context.observe(&current.position, &influence, &selected.structure);
            result["identity"] = positions::identity(&current.position);
            result["reused"] = json!(selected.reused);
            results.push(result);
        }
        json!({"results":results})
    }
}

fn terms_output(terms: &PawnTerms) -> Value {
    json!({"white":{"structureScore":terms.structure[0],"pieceTerm":terms.piece[0]},
        "black":{"structureScore":terms.structure[1],"pieceTerm":terms.piece[1]}})
}

fn subtotal_output(
    phase: Phase,
    weights: Weights,
    terms: &PawnTerms,
    scores: [i32; 2],
    ending: i32,
    progress: i32,
) -> Value {
    json!({"candidateScores":{"white":scores[0],"black":scores[1]},
        "endingScore":ending,"weightedStructure":native::structure_weighted(phase, terms.structure, terms.piece, weights.structure),
        "weightedProgress":progress,"relationQueries":terms.relation_queries})
}

fn fresh_output(
    position: &Position,
    influence: &Influence,
    phase: Phase,
    material: i32,
    weights: Weights,
    order: &[Vec<Square>; 2],
) -> Value {
    let structure =
        pawn_structure::fresh_with_order(position, influence, [&order[0], &order[1]], [1024; 2]);
    selected_output(position, influence, phase, material, weights, &structure)
}

/// Consume exactly the native selected entry, including collision-retained
/// categories/file geometry. Current membership, phase, fallback and charges
/// stay inside the native terms/progress owners.
fn selected_output(
    position: &Position,
    influence: &Influence,
    phase: Phase,
    material: i32,
    weights: Weights,
    structure: &pawn_structure::PawnStructure,
) -> Value {
    let terms = pawn_terms::compute_with_phase(position, influence, structure, phase);
    let progress = native::selected(
        position,
        influence,
        structure,
        phase,
        material,
        weights.progress,
    );
    let mut output = subtotal_output(
        phase,
        weights,
        &terms,
        [progress.paths[0].score, progress.paths[1].score],
        progress.ending,
        progress.weighted,
    );
    output["terms"] = terms_output(&terms);
    // Serialize the same native membership filter/order consumed by selected.
    // This uncharged extraction never recomputes candidate races or relations.
    let mut candidates = [Vec::new(), Vec::new()];
    for side in [Color::White, Color::Black] {
        let mut squares = [Square(0); 8];
        let len = native::current_candidates(position, structure, side, &mut squares);
        candidates[side.index()] = squares[..len].iter().map(ToString::to_string).collect::<Vec<_>>();
    }
    output["candidates"] = json!({"white":candidates[0],"black":candidates[1]});
    output
}

struct PhaseQuery {
    position: Position,
    phase: Phase,
}

impl PhaseQuery {
    fn parse(query: &Value, derived: bool) -> Result<Self> {
        object(
            query,
            if derived {
                &["placement"]
            } else {
                &["placement", "phase"]
            },
        )?;
        let position = positions::placement(&query["placement"], true)?;
        let phase = if derived {
            position.phase()
        } else {
            phase(&query["phase"])?
        };
        Ok(Self { position, phase })
    }

    fn observe(self) -> Value {
        let influence = Influence::build(&self.position);
        let structure = pawn_structure::fresh(&self.position, &influence, [1024; 2]);
        let terms =
            pawn_terms::compute_with_phase(&self.position, &influence, &structure, self.phase);
        let mut output = terms_output(&terms);
        output["phase"] = positions::phase_value(self.phase);
        output["relationQueries"] = json!(terms.relation_queries);
        output
    }
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    match operation {
        "evaluation.retainedPawnSubtotal" => return retained_subtotals(input),
        "evaluation.searchPawnSequence" => return Ok(SearchSequence::parse(input)?.observe()),
        _ => {}
    }
    object(input, &["queries"])?;
    let queries = array(&input["queries"], 1, 4096)?;
    // Collect every parsed query before producing influence or selecting work.
    let results: Vec<Value> = match operation {
        "evaluation.pawnPhase" | "evaluation.positionPawnPhase" => queries
            .iter()
            .map(|query| PhaseQuery::parse(query, operation == "evaluation.positionPawnPhase"))
            .collect::<Result<Vec<_>>>()?
            .into_iter()
            .map(PhaseQuery::observe)
            .collect(),
        "evaluation.pawnSubtotal" | "evaluation.candidatePawnSubtotal" => queries
            .iter()
            .map(|query| Subtotal::parse(query, operation == "evaluation.candidatePawnSubtotal"))
            .collect::<Result<Vec<_>>>()?
            .into_iter()
            .map(Subtotal::observe)
            .collect(),
        "evaluation.freshPawnSubtotal" => queries
            .iter()
            .map(Fresh::parse)
            .collect::<Result<Vec<_>>>()?
            .into_iter()
            .map(Fresh::observe)
            .collect(),
        "evaluation.contextPawnSubtotal" => queries
            .iter()
            .map(Context::parse)
            .collect::<Result<Vec<_>>>()?
            .into_iter()
            .map(Context::observe)
            .collect(),
        _ => {
            return Err(format!(
                "unsupported fresh pawn-subtotal operation: {operation}"
            ))
        }
    };
    Ok(json!({"results":results}))
}

#[cfg(test)]
mod tests {
    use super::*;

    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR";
    const TIED: &str = "8/P1P5/8/8/3K3k/8/p7/8";

    fn ordinary_weights() -> Value {
        json!({"white":{"structure":1024,"progress":1024},
            "black":{"structure":1024,"progress":1024}})
    }

    fn supplied() -> Value {
        json!({"placement":"7k/8/4p3/3P4/8/8/8/K7",
            "phase":{"opening":256,"middlegame":0,"endgame":0},"materialScore":17,
            "weights":ordinary_weights(),"terms":{
                "white":{"structureScore":-8,"pieceTerm":0,"candidateScore":0},
                "black":{"structureScore":0,"pieceTerm":0,"candidateScore":0}},"endingScore":-37})
    }

    fn fresh() -> Value {
        json!({"placement":TIED,"phase":{"opening":0,"middlegame":256,"endgame":0},
            "sideToMove":"white","materialScore":-10000,
            "weights":{"white":{"structure":799,"progress":1873},"black":{"structure":1321,"progress":613}},
            "pawnOrder":{"white":["a7","c7"],"black":["a2"]}})
    }

    fn context() -> Value {
        let percentages: serde_json::Map<String, Value> = scores::NAMES
            .iter()
            .map(|name| (name.to_string(), json!(100)))
            .collect();
        let mut own = Value::Object(percentages.clone());
        for name in [
            "pawn",
            "king",
            "pawnProgress",
            "pawnStructure",
            "centralInfluence",
        ] {
            own[name] = json!(1000);
        }
        json!({"rootPlacement":START,"placement":"7k/8/8/8/8/8/P7/K7",
            "rootSide":"black","sideToMove":"white","averageDepth":0,
            "percentages":{"own":own,"opponent":percentages},"pawnOrder":{"white":["a2"],"black":[]}})
    }

    #[test]
    fn phase_gate_uses_supplied_weight_and_suppresses_raw_piece_work() {
        let placement = "1r5q/8/8/3R4/8/8/P6P/K6k";
        let skipped =
            json!({"placement":placement,"phase":{"opening":0,"middlegame":16,"endgame":240}});
        let mut selected = skipped.clone();
        selected["phase"] = json!({"opening":0,"middlegame":17,"endgame":239});
        let out = dispatch(
            "evaluation.pawnPhase",
            &json!({"queries":[skipped.clone(),selected,skipped]}),
        )
        .unwrap();
        assert_eq!(out["results"][0]["white"]["pieceTerm"], 0);
        assert_eq!(out["results"][0]["relationQueries"], 0);
        assert_eq!(out["results"][1]["white"]["pieceTerm"], 1);
        assert_eq!(out["results"][1]["relationQueries"], 1);
        assert_eq!(out["results"][0], out["results"][2]);
        let derived = dispatch(
            "evaluation.positionPawnPhase",
            &json!({"queries":[{"placement":placement}]}),
        )
        .unwrap();
        assert_eq!(derived["results"][0], out["results"][0]);
    }

    #[test]
    fn supplied_terms_keep_separate_signed_rounding_without_fresh_replacement() {
        let negative = supplied();
        let mut positive = negative.clone();
        positive["terms"]["white"]["structureScore"] = json!(8);
        let mut negative_weight = negative.clone();
        negative_weight["phase"] = json!({"opening":0,"middlegame":0,"endgame":256});
        negative_weight["materialScore"] = json!(1);
        negative_weight["terms"]["white"]["structureScore"] = json!(0);
        negative_weight["terms"]["black"]["candidateScore"] = json!(4096);
        negative_weight["weights"]["black"]["progress"] = json!(-512);
        negative_weight["endingScore"] = json!(0);
        let mut positive_weight = negative_weight.clone();
        positive_weight["weights"]["black"]["progress"] = json!(512);
        let out = dispatch(
            "evaluation.pawnSubtotal",
            &json!({"queries":[negative,positive,negative_weight,positive_weight]}),
        )
        .unwrap();
        assert_eq!(out["results"][0]["weightedStructure"], -6);
        assert_eq!(out["results"][1]["weightedStructure"], 7);
        assert_eq!(out["results"][0]["endingScore"], -37);
        assert_eq!(out["results"][0]["weightedProgress"], 0);
        assert_eq!(out["results"][2]["weightedProgress"], 2048);
        assert_eq!(out["results"][3]["weightedProgress"], -2052);
        for result in out["results"].as_array().unwrap() {
            assert_eq!(result["relationQueries"], 0);
        }
    }

    #[test]
    fn supplied_candidates_allow_empty_subsets_and_fallback_uses_actual_counts() {
        let mut q = supplied();
        q.as_object_mut().unwrap().remove("endingScore");
        for name in COLORS {
            q["terms"][name]
                .as_object_mut()
                .unwrap()
                .remove("candidateScore");
        }
        q["placement"] = json!("7k/8/8/8/8/8/P7/K7");
        q["sideToMove"] = json!("black");
        q["candidates"] = json!({"white":[],"black":[]});
        q["terms"]["white"]["pieceTerm"] = json!(4096);
        let out = dispatch(
            "evaluation.candidatePawnSubtotal",
            &json!({"queries":[q.clone()]}),
        )
        .unwrap();
        assert_eq!(
            out["results"][0]["candidateScores"],
            json!({"white":0,"black":0})
        );
        assert_eq!(out["results"][0]["endingScore"], 100);
        assert_eq!(out["results"][0]["relationQueries"], 0);
        // Diagnostic candidates are supplied subsets, independent of fresh
        // classification; this a2 pawn is blocked by an opposing a3 pawn.
        q["placement"] = json!("7k/8/8/8/8/p7/P7/K7");
        q["candidates"]["white"] = json!(["a2"]);
        assert!(dispatch("evaluation.candidatePawnSubtotal", &json!({"queries":[q]})).is_ok());
    }

    #[test]
    fn explicit_fresh_order_controls_terminal_ties_before_fallback() {
        let first = fresh();
        let mut reversed = first.clone();
        reversed["pawnOrder"]["white"] = json!(["c7", "a7"]);
        let out = dispatch(
            "evaluation.freshPawnSubtotal",
            &json!({"queries":[first.clone(),reversed,first]}),
        )
        .unwrap();
        assert_eq!(
            out["results"][0]["candidates"]["white"],
            json!(["a7", "c7"])
        );
        assert_eq!(
            out["results"][1]["candidates"]["white"],
            json!(["c7", "a7"])
        );
        assert_eq!(out["results"][0]["endingScore"], 400);
        assert_eq!(out["results"][1]["endingScore"], 100);
        assert_eq!(out["results"][0]["weightedProgress"], 500);
        assert_eq!(out["results"][1]["weightedProgress"], 350);
        assert_eq!(
            out["results"][0]["candidateScores"],
            json!({"white":289,"black":138})
        );
        assert_eq!(
            out["results"][0]["candidateScores"],
            out["results"][1]["candidateScores"]
        );
        assert_eq!(out["results"][0], out["results"][2]);
    }

    #[test]
    fn context_binds_root_ownership_while_current_phase_and_turn_stay_independent() {
        let black_root = context();
        let mut white_root = black_root.clone();
        white_root["rootSide"] = json!("white");
        let mut black_turn = black_root.clone();
        black_turn["sideToMove"] = json!("black");
        let out = dispatch(
            "evaluation.contextPawnSubtotal",
            &json!({"queries":[black_root,white_root,black_turn]}),
        )
        .unwrap();
        assert_eq!(
            out["results"][0]["rootPhase"],
            json!({"opening":256,"middlegame":0,"endgame":0})
        );
        assert_eq!(
            out["results"][0]["currentPhase"],
            json!({"opening":0,"middlegame":0,"endgame":256})
        );
        assert_eq!(out["results"][0]["materialScore"], 66);
        assert_eq!(out["results"][1]["materialScore"], 660);
        assert_eq!(out["results"][2]["materialScore"], 66);
        assert_eq!(out["results"][0]["pawn"]["weightedStructure"], -9);
        assert_eq!(out["results"][1]["pawn"]["weightedStructure"], -95);
        assert_eq!(
            out["results"][0]["central"],
            json!({"white":0,"black":0,"weighted":0})
        );
        // Percent 1000 produces 10240 here. The direct supplied-weight route
        // continues to reject that coefficient as outside its own domain.
        let mut direct = fresh();
        direct["weights"]["white"]["structure"] = json!(10240);
        assert!(dispatch("evaluation.freshPawnSubtotal", &json!({"queries":[direct]})).is_err());
    }

    #[test]
    fn validation_checks_ignored_fields_complete_orders_and_strict_operation_shapes() {
        let mut invalid = context();
        invalid["percentages"]["own"]["king"] = json!(1001);
        assert!(dispatch(
            "evaluation.contextPawnSubtotal",
            &json!({"queries":[invalid]})
        )
        .is_err());
        for order in [
            json!([]),
            json!(["a7", "a7"]),
            json!(["a7", "a2"]),
            json!(["a7", "d4"]),
        ] {
            let mut q = fresh();
            q["pawnOrder"]["white"] = order;
            assert!(dispatch(
                "evaluation.freshPawnSubtotal",
                &json!({"queries":[fresh(),q]})
            )
            .is_err());
        }
        let mut q = supplied();
        q["terms"]["black"]["pieceTerm"] = json!(-1);
        assert!(dispatch("evaluation.pawnSubtotal", &json!({"queries":[q]})).is_err());
        let q = json!({"placement":"8/8/8/8/8/8/8/Kk6"});
        assert!(dispatch(
            "evaluation.positionPawnPhase",
            &json!({"queries":[q.clone()]})
        )
        .is_ok());
        let mut extra = q;
        extra["phase"] = json!({"opening":0,"middlegame":0,"endgame":256});
        assert!(dispatch("evaluation.positionPawnPhase", &json!({"queries":[extra]})).is_err());
        let mut malformed_phase = fresh();
        malformed_phase["phase"]["endgame"] = json!(1);
        assert!(dispatch(
            "evaluation.freshPawnSubtotal",
            &json!({"queries":[malformed_phase]})
        )
        .is_err());
    }

    #[test]
    fn fresh_queries_do_not_reuse_zero_or_colliding_pawn_identities() {
        let placements = [
            "7k/6P1/1p1pP3/4pP2/8/2p5/4P3/K7",
            "7k/8/2p4P/2p5/7P/1p6/p5PP/K7",
            "7k/8/8/8/8/8/8/K7",
        ];
        let mut queries = Vec::new();
        let mut identities = Vec::new();
        for placement in placements {
            let position = positions::placement(&json!(placement), true).unwrap();
            identities.push(position.pawn);
            let names = |side| {
                position
                    .piece_squares(side, PieceKind::Pawn)
                    .iter()
                    .map(|square| square.to_string())
                    .collect::<Vec<_>>()
            };
            let mut q = fresh();
            q["placement"] = json!(placement);
            q["pawnOrder"] = json!({"white":names(Color::White),"black":names(Color::Black)});
            queries.push(q);
        }
        assert_eq!(identities[0], identities[1]);
        assert_eq!(identities[2], 0);
        queries.push(queries[0].clone());
        let out = dispatch("evaluation.freshPawnSubtotal", &json!({"queries":queries})).unwrap();
        assert_ne!(out["results"][0], out["results"][1]);
        assert_eq!(out["results"][0], out["results"][3]);
        assert_eq!(
            out["results"][2]["terms"],
            json!({"white":{"structureScore":0,"pieceTerm":0},"black":{"structureScore":0,"pieceTerm":0}})
        );
        assert_eq!(
            out["results"][2]["candidates"],
            json!({"white":[],"black":[]})
        );
    }
}


#[cfg(test)]
mod retained_search_tests {
    use super::*;

    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR";
    const TIED: &str = "8/P1P5/8/8/3K3k/8/p7/8";

    fn ordered(placement: &str, side: &str, white: &[&str], black: &[&str]) -> Value {
        json!({"placement":placement,"sideToMove":side,"pawnOrder":{"white":white,"black":black}})
    }

    fn retained(mut position: Value, clear: bool) -> Value {
        position["clear"] = json!(clear);
        position["phase"] = json!({"opening":0,"middlegame":128,"endgame":128});
        position["materialScore"] = json!(17);
        position["weights"] = json!({"white":{"structure":799,"progress":1873},
            "black":{"structure":1321,"progress":613}});
        position
    }

    fn search(positions: Vec<Value>, side: &str) -> Value {
        let owner = |offset| Value::Object(scores::NAMES.iter().enumerate()
            .map(|(index, name)| (name.to_string(), json!(100 + index + offset))).collect());
        json!({"rootSide":side,"averageDepth":7,
            "percentages":{"own":owner(0),"opponent":owner(7)},"positions":positions})
    }

    fn run_retained(steps: Vec<Value>) -> Value {
        dispatch("evaluation.retainedPawnSubtotal", &json!({"steps":steps})).unwrap()["results"].clone()
    }

    fn run_search(input: &Value) -> Value {
        dispatch("evaluation.searchPawnSequence", input).unwrap()["results"].clone()
    }

    #[test]
    fn retained_order_survives_reuse_until_clear_and_next_request_starts_empty() {
        let a = retained(ordered(TIED, "white", &["a7", "c7"], &["a2"]), false);
        let b = retained(ordered(TIED, "white", &["c7", "a7"], &["a2"]), false);
        let mut cleared = b.clone();
        cleared["clear"] = json!(true);
        let out = run_retained(vec![a.clone(), b.clone(), cleared, a]);
        assert_eq!(out[0]["reused"], false);
        assert_eq!(out[1]["reused"], true);
        assert_eq!(out[1]["pawn"]["candidates"]["white"], json!(["a7", "c7"]));
        assert_eq!(out[1]["pawn"]["endingScore"], 400);
        assert_eq!(out[2]["reused"], false);
        assert_eq!(out[2]["pawn"]["endingScore"], 100);
        assert_eq!(out[3]["pawn"]["candidates"]["white"], json!(["c7", "a7"]));
        assert_eq!(out[3]["pawn"]["endingScore"], 100);
        let isolated = run_retained(vec![b]);
        assert_eq!(isolated[0]["reused"], false);
        assert_eq!(isolated[0]["pawn"], out[2]["pawn"]);
    }

    #[test]
    fn full_collision_keeps_base_piece_geometry_but_filters_current_candidates() {
        // Released collision-pieces-0-N-16: distinct arrangements have the same
        // full pawn identity. The fresh-current terms distinguish a rebuild.
        let a = retained(ordered("7k/6P1/Np1pPn2/4pP2/8/2p5/4P3/K7", "white",
            &["g7", "e6", "f5", "e2"], &["b6", "d6", "e5", "c3"]), true);
        let b = retained(ordered("7k/8/N1p2n1P/2p5/7P/1p6/p5PP/K7", "white",
            &["h2", "g2", "h4", "h6"], &["a2", "b3", "c5", "c6"]), false);
        let mut fresh_b = b.clone(); fresh_b["clear"] = json!(true);
        let out = run_retained(vec![a, b.clone(), fresh_b]);
        assert_eq!(out[0]["identity"]["pawn"], out[1]["identity"]["pawn"]);
        assert_ne!(out[0]["identity"]["secondary"], out[1]["identity"]["secondary"]);
        assert_eq!(out[1]["reused"], true);
        assert_eq!(out[1]["pawn"]["terms"]["white"]["structureScore"], -19);
        assert_eq!(out[1]["pawn"]["terms"]["black"]["pieceTerm"], 1);
        assert_eq!(out[1]["pawn"]["candidates"], json!({"white":[],"black":[]}));
        assert_eq!(out[2]["pawn"]["terms"]["white"]["structureScore"], -28);
        assert_eq!(out[2]["pawn"]["terms"]["black"]["pieceTerm"], 0);
        let isolated = run_retained(vec![b]);
        assert_eq!(isolated[0]["pawn"], out[2]["pawn"]);
    }

    #[test]
    fn repeated_hits_recompute_phase_selected_piece_work_even_with_zero_weights() {
        let mut gated = retained(ordered("1r5q/8/8/3R4/8/8/P6P/K6k", "white",
            &["a2", "h2"], &[]), false);
        gated["phase"] = json!({"opening":0,"middlegame":16,"endgame":240});
        gated["weights"] = json!({"white":{"structure":0,"progress":0},"black":{"structure":0,"progress":0}});
        let mut active = gated.clone();
        active["phase"] = json!({"opening":17,"middlegame":0,"endgame":239});
        let out = run_retained(vec![gated.clone(), active.clone(), active, gated]);
        assert_eq!(out[0]["pawn"]["relationQueries"], 0);
        assert_eq!(out[1]["reused"], true);
        assert_eq!(out[1]["pawn"]["terms"]["white"]["pieceTerm"], 1);
        assert_eq!(out[1]["pawn"]["relationQueries"], 1);
        assert_eq!(out[2]["pawn"]["relationQueries"], 1);
        assert_eq!(out[1]["pawn"], out[2]["pawn"]);
        assert_eq!(out[3]["pawn"]["relationQueries"], 0);
        assert_eq!(out[3]["pawn"]["terms"]["white"]["pieceTerm"], 0);
    }

    #[test]
    fn search_root_context_stays_fixed_across_current_side_phase_and_count_changes() {
        for side in ["white", "black"] {
            let root = ordered(START, side, &["a2","b2","c2","d2","e2","f2","g2","h2"],
                &["a7","b7","c7","d7","e7","f7","g7","h7"]);
            let a = ordered("7k/8/8/8/8/8/P7/K7", "white", &["a2"], &[]);
            let b = ordered("7k/8/8/8/8/8/P7/K7", "black", &["a2"], &[]);
            let mut input = search(vec![root.clone(), a.clone(), b.clone()], side);
            input["averageDepth"] = json!(-100);
            for owner in ["own", "opponent"] {
                for name in scores::NAMES { input["percentages"][owner][name] = json!(1000); }
            }
            // Ownership is asymmetric, and produced coefficients reach 10240.
            input["percentages"]["opponent"]["pawnStructure"] = json!(0);
            let out = run_search(&input);
            for (index, current) in [root, a, b].iter().enumerate() {
                let query = json!({"rootPlacement":START,"placement":current["placement"],
                    "rootSide":side,"sideToMove":current["sideToMove"],"averageDepth":-100,
                    "percentages":input["percentages"],"pawnOrder":current["pawnOrder"]});
                let expected = dispatch("evaluation.contextPawnSubtotal", &json!({"queries":[query]})).unwrap();
                for field in ["rootPhase", "currentPhase", "materialScore", "pawn", "central"] {
                    assert_eq!(out[index][field], expected["results"][0][field], "{side}/{index}/{field}");
                }
            }
            assert_eq!(out[1]["rootPhase"], json!({"opening":256,"middlegame":0,"endgame":0}));
            assert_eq!(out[1]["currentPhase"], json!({"opening":0,"middlegame":0,"endgame":256}));
            assert_eq!(out[1]["materialScore"], out[2]["materialScore"]);
            assert_eq!(out[2]["reused"], true);
        }
    }

    #[test]
    fn search_collision_retains_structure_but_uses_current_piece_positions_and_fresh_request_state() {
        let a = ordered("1q5k/6P1/Np1pPn2/4pP2/8/2p5/4P3/KQ6", "white",
            &["g7","e6","f5","e2"], &["b6","d6","e5","c3"]);
        let b = ordered("1q5k/8/N1p2n1P/2p5/7P/1p6/p5PP/KQ6", "white",
            &["h2","g2","h4","h6"], &["a2","b3","c5","c6"]);
        let input = search(vec![a.clone(), b.clone(), b.clone(), a], "white");
        let out = run_search(&input);
        assert_eq!(out[0]["reused"], false);
        assert_eq!(out[1]["reused"], true);
        assert_eq!(out[1]["identity"]["pawn"], out[0]["identity"]["pawn"]);
        assert_eq!(out[0]["pawn"]["terms"]["black"]["pieceTerm"], 1);
        assert_eq!(out[1]["pawn"]["terms"]["black"]["pieceTerm"], 0);
        assert_eq!(out[1]["pawn"]["terms"]["white"]["structureScore"], -19);
        assert_eq!(out[1]["pawn"]["candidates"], json!({"white":[],"black":[]}));
        assert_eq!(out[1], out[2]);
        assert_eq!(run_search(&input), out);
        let isolated = run_search(&search(vec![b], "white"));
        assert_eq!(isolated[0]["reused"], false);
        assert_ne!(isolated[0]["pawn"]["terms"], out[1]["pawn"]["terms"]);
    }

    #[test]
    fn pawnless_zero_identity_is_reused_against_cleared_state_in_each_operation() {
        let position = ordered("7k/8/8/8/8/8/8/K7", "black", &[], &[]);
        let a = run_retained(vec![retained(position.clone(), true)]);
        let b = run_search(&search(vec![position], "black"));
        for result in [&a[0], &b[0]] {
            assert_eq!(result["identity"]["pawn"], 0);
            assert_eq!(result["reused"], true);
            assert_eq!(result["pawn"]["terms"], json!({"white":{"structureScore":0,"pieceTerm":0},"black":{"structureScore":0,"pieceTerm":0}}));
            assert_eq!(result["pawn"]["candidates"], json!({"white":[],"black":[]}));
            assert_eq!(result["pawn"]["relationQueries"], 0);
        }
    }

    #[test]
    fn retained_whole_schema_and_late_ignored_context_fields_validate_before_state() {
        let good = retained(ordered(TIED, "white", &["a7","c7"], &["a2"]), false);
        for (field, value) in [("clear",json!(1)), ("phase",json!({"opening":0,"middlegame":16,"endgame":239})),
            ("materialScore",json!(10001)), ("rootSide",json!("white")), ("sideToMove",json!("White"))] {
            let mut bad = good.clone(); bad[field] = value;
            assert!(RetainedStep::parse(&json!({"steps":[good.clone(),bad]})).is_err(), "{field}");
        }
        for order in [json!(["a7"]),json!(["a7","a7"]),json!(["a7","h8"])] {
            let mut bad = good.clone(); bad["pawnOrder"]["white"] = order;
            assert!(RetainedStep::parse(&json!({"steps":[good.clone(),bad]})).is_err());
        }
        let mut bad = good.clone(); bad["weights"]["black"]["progress"] = json!(10001);
        bad["phase"] = json!({"opening":256,"middlegame":0,"endgame":0});
        assert!(RetainedStep::parse(&json!({"steps":[good.clone(),bad]})).is_err());
        assert!(RetainedStep::parse(&json!({"steps":[]})).is_err());
        assert!(RetainedStep::parse(&json!({"steps":vec![good;4097]})).is_err());
    }

    #[test]
    fn search_rejects_late_fields_incomplete_percentages_and_root_mismatch_before_context() {
        let position = ordered(TIED, "white", &["a7","c7"], &["a2"]);
        let good = search(vec![position.clone(), position], "white");
        for field in ["phase","weights","materialScore","clear","rootSide"] {
            let mut bad = good.clone(); bad["positions"][1][field] = Value::Null;
            assert!(SearchSequence::parse(&bad).is_err(), "{field}");
        }
        for value in [json!(-1),json!(1001),json!(1.5),Value::Null] {
            let mut bad = good.clone(); bad["percentages"]["opponent"]["king"] = value;
            assert!(SearchSequence::parse(&bad).is_err());
        }
        let mut bad = good.clone(); bad["percentages"]["own"].as_object_mut().unwrap().remove("mobility");
        assert!(SearchSequence::parse(&bad).is_err());
        let mut bad = good.clone(); bad["positions"][1]["pawnOrder"]["white"] = json!(["a7"]);
        assert!(SearchSequence::parse(&bad).is_err());
        let mut bad = good.clone(); bad["rootSide"] = json!("black");
        assert!(SearchSequence::parse(&bad).is_err());
        let mut bad = good.clone(); bad["averageDepth"] = json!(101);
        assert!(SearchSequence::parse(&bad).is_err());
        let mut bad = good.clone(); bad["positions"] = json!([]);
        assert!(SearchSequence::parse(&bad).is_err());
        let mut bad = good.clone(); bad["positions"] = json!(vec![good["positions"][0].clone();4097]);
        assert!(SearchSequence::parse(&bad).is_err());
    }

    #[test]
    fn component_placements_admit_adjacent_kings_but_keep_bounded_material_limits() {
        let adjacent = ordered("8/8/8/8/8/8/k7/K7", "white", &[], &[]);
        assert!(SearchSequence::parse(&search(vec![adjacent.clone()], "white")).is_ok());
        assert!(RetainedStep::parse(&json!({"steps":[retained(adjacent,false)]})).is_ok());
        for placement in ["P6k/8/8/8/8/8/8/K7", "7k/8/8/8/8/NNNNNNNN/NNN5/K7",
            "7k/8/8/8/8/8/PPPPPPPP/KP6"] {
            let bad = ordered(placement, "white", &[], &[]);
            assert!(SearchSequence::parse(&search(vec![bad.clone()], "white")).is_err());
            assert!(RetainedStep::parse(&json!({"steps":[retained(bad,false)]})).is_err());
        }
    }
}
