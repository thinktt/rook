//! Cold external JSON adapter. All specified calculations call the native library.
use rook2::{
    clock::{Schedule, Stage},
    evaluation, ordinary_policy, output,
    parameters::Parameters,
    position::Phase,
    types::Color,
};
use serde_json::{json, Map, Value};
use std::{
    io::{self, BufRead, Write},
    process::ExitCode,
};

mod admission;
mod boundary_admission;
mod candidate_order;
mod endgame_bounds;
mod endings;
mod evaluation_common;
mod fresh_evaluation;
mod king_shelter;
mod learned;
mod ledger;
mod move_evaluation;
mod moves;
mod ordering;
mod pawn_fresh;
mod pawn_progress;
mod pawn_retained;
mod pawn_subtotals;
mod policies;
mod position_terms;
mod positions;
mod quiescence_evaluation;
mod quiescence_tree;
mod relations;
mod retained_evaluation;
mod root_context;
mod score_context;
mod scores;
mod supplied;
mod threat;

type Result<T> = std::result::Result<T, String>;

fn object<'a>(v: &'a Value, keys: &[&str]) -> Result<&'a Map<String, Value>> {
    let map = v.as_object().ok_or("expected object")?;
    if map.len() != keys.len() || keys.iter().any(|key| !map.contains_key(*key)) {
        return Err(format!("expected exactly fields {keys:?}"));
    }
    Ok(map)
}
fn array(v: &Value, minimum: usize, maximum: usize) -> Result<&[Value]> {
    let values = v.as_array().ok_or("expected array")?;
    if !(minimum..=maximum).contains(&values.len()) {
        return Err("array length outside operation domain".into());
    }
    Ok(values)
}
fn text(v: &Value) -> Result<&str> {
    v.as_str().ok_or_else(|| "expected string".into())
}
fn boolean(v: &Value) -> Result<bool> {
    v.as_bool().ok_or_else(|| "expected boolean".into())
}
fn integer(v: &Value, minimum: i32, maximum: i32) -> Result<i32> {
    let number = v.as_f64().ok_or("expected integer")?;
    if !number.is_finite()
        || number.fract() != 0.0
        || number < minimum as f64
        || number > maximum as f64
    {
        return Err(format!("integer outside {minimum}..{maximum}"));
    }
    Ok(number as i32)
}
fn unsigned32(v: &Value) -> Result<u32> {
    let number = v.as_f64().ok_or("expected unsigned integer")?;
    if !number.is_finite() || number.fract() != 0.0 || !(0.0..=u32::MAX as f64).contains(&number) {
        return Err("integer outside unsigned32 domain".into());
    }
    Ok(number as u32)
}
fn color(v: &Value) -> Result<Color> {
    match text(v)? {
        "white" => Ok(Color::White),
        "black" => Ok(Color::Black),
        _ => Err("invalid color".into()),
    }
}
fn phase(v: &Value) -> Result<Phase> {
    object(v, &["opening", "middlegame", "endgame"])?;
    let p = Phase {
        opening: integer(&v["opening"], 0, 256)? as u16,
        middlegame: integer(&v["middlegame"], 0, 256)? as u16,
        endgame: integer(&v["endgame"], 0, 256)? as u16,
    };
    if p.opening as u32 + p.middlegame as u32 + p.endgame as u32 != 256 {
        return Err("phase must total 256".into());
    }
    Ok(p)
}
fn schedule(v: &Value) -> Result<Schedule> {
    let mut stages = Vec::new();
    for stage in array(v, 1, 2)? {
        object(stage, &["moves", "baseSeconds", "incrementSeconds"])?;
        stages.push(Stage {
            moves: integer(&stage["moves"], 1, 10000)? as u32,
            base_seconds: integer(&stage["baseSeconds"], 0, 3600)? as u32,
            increment_seconds: integer(&stage["incrementSeconds"], 0, 60)? as u32,
        });
    }
    Ok(Schedule { stages })
}

fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    match operation {
        "evaluation.kingShelter" => king_shelter::run(input),
        "evaluation.materialValues"
        | "evaluation.rootMaterial"
        | "evaluation.squareValues"
        | "evaluation.squareBalance" => root_context::dispatch(operation, input),
        "evaluation.materialThreat" | "search.fastThreat" => threat::dispatch(operation, input),
        "evaluation.pawnRaceBounds"
        | "evaluation.endgameAdjust"
        | "evaluation.fortressBounds"
        | "evaluation.rookFortress" => endgame_bounds::dispatch(operation, input),
        "search.quiescenceTree" => quiescence_tree::dispatch(input),
        "evaluation.moveSequence" => move_evaluation::dispatch(input),
        "evaluation.retainedSequence" => retained_evaluation::dispatch(input),
        "evaluation.quiescenceEntry" | "evaluation.quiescenceDisposition" => {
            quiescence_evaluation::dispatch(operation, input)
        }
        "evaluation.freshSubtotal" | "evaluation.freshScore" => {
            fresh_evaluation::dispatch(operation, input)
        }
        "evaluation.scoreContext" | "evaluation.personalityScore" | "evaluation.positionScore" => {
            score_context::dispatch(operation, input)
        }
        "evaluation.scoreFinish"
        | "evaluation.finalScore"
        | "evaluation.personalityWeights"
        | "evaluation.personalityCentralBalance" => scores::dispatch(operation, input),
        "evaluation.endgamePawnSpread"
        | "evaluation.pawnlessPotential"
        | "evaluation.minorMateGeometry"
        | "evaluation.endgameMaterialBlend"
        | "evaluation.pawnRace" => endings::dispatch(operation, input),
        "search.drawBoundary" | "search.moveReversal" | "search.mateLeaf" | "search.mateLeafPosition" => {
            boundary_admission::dispatch(operation, input)
        }
        "search.nodeAdmission" | "search.historyAdmission" | "search.moveExtensions" => {
            admission::dispatch(operation, input)
        }
        "evaluation.materialBalance"
        | "search.captureException"
        | "search.captureDefense"
        | "search.squareCaptureDefense"
        | "search.quiescenceCaptureAllowance"
        | "search.frontierEstimate"
        | "search.kingPressure"
        | "search.fastCutoff" => supplied::dispatch(operation, input),
        "search.rootRandomization"
        | "search.rootAspiration"
        | "search.quiescenceCapturePolicy"
        | "output.pvLine" => policies::dispatch(operation, input),
        "ordering.prioritySequence" | "tactics.capturePreferenceOrder" => {
            ordering::dispatch(operation, input)
        }
        "search.orderCandidates" => candidate_order::dispatch(input),
        "clock.workSequence" => ledger::dispatch(input),
        "search.cutoffMemory" | "search.rememberedResults" => learned::dispatch(operation, input),
        "evaluation.retainedPawnStructure" | "evaluation.retainedPawnCandidates" => {
            pawn_retained::dispatch(operation, input)
        }
        "evaluation.pawnPhase"
        | "evaluation.positionPawnPhase"
        | "evaluation.pawnSubtotal"
        | "evaluation.candidatePawnSubtotal"
        | "evaluation.freshPawnSubtotal"
        | "evaluation.contextPawnSubtotal"
        | "evaluation.retainedPawnSubtotal"
        | "evaluation.searchPawnSequence" => pawn_subtotals::dispatch(operation, input),
        "evaluation.pawnStructure"
        | "evaluation.pawnPressure"
        | "evaluation.pawnStructureScore"
        | "evaluation.pawnPiece" => pawn_fresh::dispatch(operation, input),
        "evaluation.pawnProgress"
        | "evaluation.pawnCandidates"
        | "evaluation.pawnCandidateEnding"
        | "evaluation.pawnEnding" => pawn_progress::dispatch(operation, input),
        "evaluation.activity"
        | "evaluation.boardPatterns"
        | "evaluation.centralInfluenceBalance"
        | "evaluation.positionCentralBalance" => position_terms::dispatch(operation, input),
        "evaluation.relations"
        | "evaluation.adjustedRelations"
        | "evaluation.squareRelations"
        | "evaluation.influence" => relations::dispatch(operation, input),
        "position.setup"
        | "position.setupMoveSequence"
        | "position.moveSequence"
        | "position.identity"
        | "evaluation.phase" => positions::dispatch(operation, input),
        "time.schedule" => {
            object(input, &["stages", "moveIndex"])?;
            let seconds = schedule(&input["stages"])?
                .seconds(integer(&input["moveIndex"], 0, 10000)? as u64)
                .map_err(|e| format!("schedule: {e:?}"))?;
            Ok(json!({"seconds":seconds}))
        }
        "time.allowance" => {
            object(
                input,
                &[
                    "stages",
                    "gamePly",
                    "adjustmentCs",
                    "searchOptimism",
                    "pondering",
                ],
            )?;
            let allowance = schedule(&input["stages"])?
                .allowance(
                    integer(&input["gamePly"], 0, 10000)? as u32,
                    integer(&input["adjustmentCs"], -100000000, 100000000)?,
                    integer(&input["searchOptimism"], 0, 100)?,
                    boolean(&input["pondering"])?,
                )
                .map_err(|e| format!("allowance: {e:?}"))?;
            Ok(json!({"averageCs":allowance.average_cs,"maximumCs":allowance.maximum_cs}))
        }
        "session.parameters" => {
            object(input, &["commands"])?;
            let mut parameters = Parameters::default();
            let mut replies = Vec::new();
            for command in array(&input["commands"], 0, usize::MAX)? {
                let command = text(command)?;
                let words: Vec<_> = command.split_ascii_whitespace().collect();
                if words.first() != Some(&"cm_parm") {
                    return Err("parameter sequence requires cm_parm".into());
                }
                replies.push(
                    parameters
                        .command(&words[1..])
                        .map_err(|e| format!("parameters: {e:?}"))?,
                );
            }
            Ok(json!({"replies":replies}))
        }
        "search.selectiveDepth" => {
            object(input, &["queries"])?;
            let mut results = Vec::new();
            for query in array(&input["queries"], 1, 4096)? {
                object(
                    query,
                    &[
                        "iterationDepth",
                        "selectivity",
                        "endgameWeight",
                        "targetPly",
                    ],
                )?;
                let v = ordinary_policy::selective_depth(
                    integer(&query["iterationDepth"], 0, 64)?,
                    integer(&query["selectivity"], i32::MIN, i32::MAX)?,
                    integer(&query["endgameWeight"], 0, 256)? as u16,
                    integer(&query["targetPly"], 0, 64)?,
                );
                results.push(json!({"nodeAdjustment":v.adjustment,"rootMateMargin":v.margin,"adjustedTarget":v.adjusted_target}));
            }
            Ok(json!({"results":results,"chargedSearchUnits":0,"chargedRelationQueries":0}))
        }
        "output.searchScore" | "output.personalitySearchScore" => {
            object(input, &["queries"])?;
            let mut results = Vec::new();
            for query in array(&input["queries"], 1, 4096)? {
                let draw = if operation == "output.searchScore" {
                    object(query, &["rankingScore", "drawPreference"])?;
                    integer(&query["drawPreference"], -10000, 10000)?
                } else {
                    object(query, &["rankingScore", "rootSide", "rootPhase", "cfd"])?;
                    color(&query["rootSide"])?;
                    evaluation::draw_preference(
                        phase(&query["rootPhase"])?,
                        integer(&query["cfd"], -10000, 10000)?,
                    )
                };
                let score =
                    output::reported_score(integer(&query["rankingScore"], -10000, 10000)?, draw);
                results.push(json!({"drawPreference":draw,"reportedScore":score}));
            }
            Ok(json!({"results":results}))
        }
        _ => Err(format!("operation not implemented: {operation}")),
    }
}

fn response(request: &Value) -> Result<Value> {
    object(request, &["version", "operation", "input"])?;
    integer(&request["version"], 1, 1)?;
    Ok(json!({"version":1,"output":dispatch(text(&request["operation"])?,&request["input"])?}))
}

fn run() -> Result<()> {
    let mut input = String::new();
    let mut reader = io::stdin().lock();
    let request = loop {
        let n = reader.read_line(&mut input).map_err(|e| e.to_string())?;
        if n == 0 || !input.ends_with('\n') {
            return Err("request must end in newline".into());
        }
        match serde_json::from_str::<Value>(&input) {
            Ok(value) => break value,
            Err(error) if error.is_eof() => continue,
            Err(error) => return Err(error.to_string()),
        }
    };
    let value = response(&request)?;
    let mut writer = io::stdout().lock();
    serde_json::to_writer(&mut writer, &value).map_err(|e| e.to_string())?;
    writer.write_all(b"\n").map_err(|e| e.to_string())?;
    writer.flush().map_err(|e| e.to_string())
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("rook2-diag: {error}");
            ExitCode::from(1)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn admission_rejects_extra_fields_and_accepts_integer_number_forms() {
        let request = json!({"version":1,"operation":"time.schedule","input":{"stages":[{"moves":1,"baseSeconds":1,"incrementSeconds":0}],"moveIndex":1.0}});
        assert_eq!(response(&request).unwrap()["output"]["seconds"], 2);
        let mut extra = request.clone();
        extra["input"]["unrelated"] = json!(0);
        assert!(response(&extra).is_err());
        let mut bad = request;
        bad["input"]["moveIndex"] = json!(1.5);
        assert!(response(&bad).is_err());
    }
    #[test]
    fn query_order_duplicates_and_signed_selectivity_are_preserved() {
        let query =
            json!({"iterationDepth":10,"selectivity":i32::MIN,"endgameWeight":0,"targetPly":64});
        let out = dispatch(
            "search.selectiveDepth",
            &json!({"queries":[query.clone(),query]}),
        )
        .unwrap();
        assert_eq!(out["results"][0], out["results"][1]);
        assert_eq!(out["results"][0]["rootMateMargin"], 1);
    }
}
