//! Fresh pawn phase/subtotal transport. Native kernels own scores and work.
use super::{array, color, integer, object, pawn_progress, phase, positions, scores, Result};
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
        let value = &query["percentages"];
        object(value, &["own", "opponent"])?;
        let mut percentages = [[0; 11]; 2];
        for (owner, side) in [("own", root.side), ("opponent", root.side.opponent())] {
            object(&value[owner], &scores::NAMES)?;
            for (index, name) in scores::NAMES.iter().enumerate() {
                percentages[side.index()][index] = integer(&value[owner][*name], 0, 1000)? as u16;
            }
        }
        Ok(Self {
            root,
            current,
            percentages,
            average_depth,
            order,
        })
    }

    fn observe(self) -> Value {
        let material_percentages = [
            std::array::from_fn(|index| self.percentages[0][index]),
            std::array::from_fn(|index| self.percentages[1][index]),
        ];
        let root = RootContext::new(&self.root, material_percentages, self.average_depth);
        let phase = self.current.phase();
        let material = root.material(&self.current);
        let pair = |index| {
            [
                evaluator::coefficient(self.percentages[0][index] as i32),
                evaluator::coefficient(self.percentages[1][index] as i32),
            ]
        };
        // Context production admits 10240; direct supplied weights stop at
        // 10000. Do not reparse produced coefficients through that narrower API.
        let weights = Weights {
            structure: pair(10),
            progress: pair(9),
        };
        let influence = Influence::build(&self.current);
        let pawn = fresh_output(
            &self.current,
            &influence,
            phase,
            material,
            weights,
            &self.order,
        );
        let central = positional_terms::central(&influence, phase, pair(6));
        json!({"rootPhase":positions::phase_value(root.phase),
            "currentPhase":positions::phase_value(phase),"materialScore":material,"pawn":pawn,
            "central":{"white":central.colors[0],"black":central.colors[1],"weighted":central.weighted}})
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
    let terms = pawn_terms::compute_with_phase(position, influence, &structure, phase);
    let progress = native::selected(
        position,
        influence,
        &structure,
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
    // This serialization follows fresh descriptor chronology. Native selected
    // consumes these same descriptors; no square/score sort changes tie order.
    output["candidates"] = json!({
        "white":structure.pawn_slice(Color::White).iter().filter(|pawn| pawn.candidate).map(|pawn| pawn.square.to_string()).collect::<Vec<_>>(),
        "black":structure.pawn_slice(Color::Black).iter().filter(|pawn| pawn.candidate).map(|pawn| pawn.square.to_string()).collect::<Vec<_>>()});
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
