from pathlib import Path
import json
E=Path(__file__).parent;N=Path(json.loads((E/'paths.json').read_text())['proposal']);p=N/'diagnostic/src/pawn_subtotals.rs';s=p.read_text()
s=s.replace('//! Fresh pawn phase/subtotal transport. Native kernels own scores and work.','//! Cold fresh/retained pawn composition. Native owners produce context, scores and work.')
s=s.replace('use super::{array, color, integer, object, pawn_progress, phase, positions, scores, Result};','use super::{array, boolean, color, integer, object, pawn_progress, phase, positions, scores, Result};')
start=s.index('impl Fresh {');at=s.index('        let mut position = positions::placement(&query["placement"], true)?;',start)
s=s[:at]+'        Self::parse_fields(query)\n    }\n\n    // The caller owns the exact object schema; all supplied fields are parsed.\n    fn parse_fields(query: &Value) -> Result<Self> {\n'+s[at:]
start=s.index('        let value = &query["percentages"];',s.index('impl Context {'));end=s.index('        Ok(Self {',start)
s=s[:start]+'        let percentages = percentages(&query["percentages"], root.side)?;\n'+s[end:]
start=s.index('    fn observe(self) -> Value {',s.index('impl Context {'));end=s.index('\nfn terms_output',start)
s=s[:start]+'''    fn observe(self) -> Value {
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
''' +s[end:]
start=s.index('    let terms = pawn_terms::compute_with_phase(position, influence, &structure, phase);',s.index('fn fresh_output('))
s=s[:start]+'''    selected_output(position, influence, phase, material, weights, &structure)
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
''' +s[start:]
s=s.replace('pawn_terms::compute_with_phase(position, influence, &structure, phase)','pawn_terms::compute_with_phase(position, influence, structure, phase)')
start=s.index('fn selected_output(');end=s.index('\nstruct PhaseQuery',start);chunk=s[start:end].replace('        &structure,','        structure,')
a=chunk.index('    // This serialization follows fresh descriptor chronology.');b=chunk.index('    output\n}',a)
chunk=chunk[:a]+'''    // Serialize the same native membership filter/order consumed by selected.
    // This uncharged extraction never recomputes candidate races or relations.
    let mut candidates = [Vec::new(), Vec::new()];
    for side in [Color::White, Color::Black] {
        let mut squares = [Square(0); 8];
        let len = native::current_candidates(position, structure, side, &mut squares);
        candidates[side.index()] = squares[..len].iter().map(ToString::to_string).collect::<Vec<_>>();
    }
    output["candidates"] = json!({"white":candidates[0],"black":candidates[1]});
''' +chunk[b:]
s=s[:start]+chunk+s[end:]
needle='pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {\n'
s=s.replace(needle,needle+'''    match operation {
        "evaluation.retainedPawnSubtotal" => return retained_subtotals(input),
        "evaluation.searchPawnSequence" => return Ok(SearchSequence::parse(input)?.observe()),
        _ => {}
    }
''')
p.write_text(s)
p=N/'diagnostic/src/main.rs';s=p.read_text();s=s.replace('        | "evaluation.contextPawnSubtotal" => pawn_subtotals::dispatch(operation, input),','        | "evaluation.contextPawnSubtotal"\n        | "evaluation.retainedPawnSubtotal"\n        | "evaluation.searchPawnSequence" => pawn_subtotals::dispatch(operation, input),');p.write_text(s)
print(N)
