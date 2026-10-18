//! Supplied material/capture contexts. Native policy owns all component kernels.
//!
//! Count-only material hypotheticals and ready-profile observations deliberately
//! need not form one consistent placement. They never enter legal move generation.
use super::{array, boolean, color, integer, moves, object, positions, relations, text, Result};
use rook2::{
    evaluation::RootContext,
    influence::{profile_sum, Influence},
    ordinary_policy,
    position::Position,
    quiescence_policy,
    types::{Color, Move, MoveKind, Piece, PieceKind, Square},
};
use serde_json::{json, Value};

const SOURCE: Square = Square(8);
const DESTINATION: Square = Square(16);

fn bare() -> Position {
    Position::from_fen("7k/8/8/8/8/8/8/K7 w - - 0 1").unwrap()
}

pub(super) fn counts(value: &Value) -> Result<[[u8; 6]; 2]> {
    object(value, &moves::COLORS)?;
    let mut result = [[0u8; 6]; 2];
    let mut total = 0u32;
    for (side, name) in moves::COLORS.iter().enumerate() {
        object(&value[*name], &moves::PIECES[..5])?;
        for (piece, name_piece) in moves::PIECES[..5].iter().enumerate() {
            let count = integer(&value[*name][*name_piece], 0, 15)? as u8;
            result[side][piece] = count;
            total += count as u32;
        }
        result[side][PieceKind::King.index()] = 1;
    }
    if total > 30 {
        return Err("material exceeds30 counted pieces across colors".into());
    }
    Ok(result)
}

fn material(value: &Value) -> Result<(RootContext, Position)> {
    object(
        value,
        &[
            "values",
            "rootCounts",
            "currentCounts",
            "rootSide",
            "averageDepth",
        ],
    )?;
    let mut position = bare();
    let mut root = RootContext::neutral(&position);
    root.side = color(&value["rootSide"])?;
    root.average_depth = integer(&value["averageDepth"], -100, 100)?;
    root.counts = counts(&value["rootCounts"])?;
    position.counts = counts(&value["currentCounts"])?;
    object(&value["values"], &moves::COLORS)?;
    for (side, name) in moves::COLORS.iter().enumerate() {
        object(&value["values"][*name], &moves::PIECES[..5])?;
        for (piece, name_piece) in moves::PIECES[..5].iter().enumerate() {
            root.values[side][piece] = integer(&value["values"][*name][*name_piece], 0, 10000)?;
        }
    }
    Ok((root, position))
}

fn promotion(value: &Value) -> Result<MoveKind> {
    if value.is_null() {
        return Ok(MoveKind::Ordinary);
    }
    let piece = moves::piece(value)?;
    if !matches!(
        piece,
        PieceKind::Knight | PieceKind::Bishop | PieceKind::Rook | PieceKind::Queen
    ) {
        return Err("invalid promotion choice".into());
    }
    Ok(MoveKind::Promotion(piece))
}

fn occupant(value: &Value, king: bool) -> Result<Piece> {
    if value.is_null() {
        return Ok(Piece::EMPTY);
    }
    object(value, &["side", "piece"])?;
    let piece = moves::piece(&value["piece"])?;
    if !king && piece == PieceKind::King {
        return Err("king is outside this captured-material domain".into());
    }
    Ok(Piece::new(color(&value["side"])?, piece))
}

pub(super) struct CaptureContext { pub position:Position, pub movement:Move }
impl CaptureContext {
    fn parse(value:&Value) -> Result<Self> {
        object(value,&["promotion","destination","material"])?;
        let kind = promotion(&value["promotion"])?;
        let mut position = bare();
        position.counts = counts(&value["material"])?;
        position.board[DESTINATION.0 as usize] = occupant(&value["destination"],true)?;
        Ok(Self { position,movement:Move::new(SOURCE,DESTINATION,kind) })
    }
    fn exception(&self) -> bool {
        quiescence_policy::capture_exception(&self.position,&self.movement)
    }
}
fn capture_exception(value:&Value) -> Result<bool> { Ok(CaptureContext::parse(value)?.exception()) }

fn capture(position: &mut Position, value: &Value, required: bool) -> Result<Piece> {
    let piece = occupant(value, false)?;
    if piece.is_empty() {
        if required {
            return Err("ordinary capture requires a victim".into());
        }
    } else if position.counts[piece.color().index()][piece.kind().index()] == 0 {
        return Err("victim is absent from current counts".into());
    }
    position.board[DESTINATION.0 as usize] = piece;
    Ok(piece)
}

struct Pressure {
    position: Position,
    previous: Influence,
    current: Influence,
    previous_pressure: Vec<u8>,
    current_pressure: Vec<u8>,
}

impl Pressure {
    fn parse(value: &Value) -> Result<Self> {
        object(value, &["side", "neighbors"])?;
        let side = color(&value["side"])?;
        // A central king supplies eight real neighbor slots. Excluded ready
        // profiles become zero only in the guard maps, not observation arrays.
        let mut position = Position::from_fen(if side == Color::White {
            "7k/8/8/8/3K4/8/8/8 w - - 0 1"
        } else {
            "7K/8/8/8/3k4/8/8/8 b - - 0 1"
        })?;
        position.side = side;
        let king = Square::parse("d4").unwrap();
        let neighbors = array(&value["neighbors"], 8, 8)?;
        let mut previous = Influence {
            profiles: [[0; 64]; 2],
        };
        let mut current = previous;
        let mut previous_pressure = Vec::new();
        let mut current_pressure = Vec::new();
        let mut index = 0;
        for dr in -1..=1 {
            for df in -1..=1 {
                if df == 0 && dr == 0 {
                    continue;
                }
                let neighbor = &neighbors[index];
                index += 1;
                object(neighbor, &["included", "previous", "current"])?;
                let included = boolean(&neighbor["included"])?;
                let before = relations::profile(&neighbor["previous"])?;
                let after = relations::profile(&neighbor["current"])?;
                previous_pressure.push(profile_sum(before));
                current_pressure.push(profile_sum(after));
                if included {
                    let square = king.offset(df, dr).unwrap().0 as usize;
                    previous.profiles[side.opponent().index()][square] = before;
                    current.profiles[side.opponent().index()][square] = after;
                }
            }
        }
        Ok(Self {
            position,
            previous,
            current,
            previous_pressure,
            current_pressure,
        })
    }

    fn guard(&self) -> bool {
        ordinary_policy::king_pressure(&self.position, &self.previous, &self.current)
    }
}

/// Shared cold controlled-response query; arithmetic and request ordering are
/// moved from the existing fastCutoff transport rather than duplicated.
pub(super) struct FastCutoff {
    pub ply:i32, pub target:i32, pub upper:i32, pub capture:CaptureContext,
    score:i32, checked:bool, previous_checked:bool, pressure:Pressure, threat:i32,
}
#[derive(Default)]
pub(super) struct FastCutoffResult {
    pub score:Option<i32>, pub pressure_checked:bool, pub threat_queried:bool,
}
impl FastCutoffResult {
    pub(super) fn output(&self) -> Value {
        json!({"cutoffScore":self.score,"pressureChecked":self.pressure_checked,
            "materialThreatQueried":self.threat_queried})
    }
}
impl FastCutoff {
    pub(super) fn parse(query:&Value) -> Result<Self> {
        object(query,&["searchPly","targetPly","staticScore","upperBound","currentCheck",
            "previousCheck","capture","pressure","materialThreat"])?;
        let ply = integer(&query["searchPly"],1,62)?;
        Ok(Self { ply,target:integer(&query["targetPly"],ply+1,64)?,
            score:integer(&query["staticScore"],-10000,10000)?,
            upper:integer(&query["upperBound"],-9999,10000)?,
            checked:boolean(&query["currentCheck"])?,previous_checked:boolean(&query["previousCheck"])?,
            capture:CaptureContext::parse(&query["capture"])?,pressure:Pressure::parse(&query["pressure"])?,
            threat:integer(&query["materialThreat"],0,20000)? })
    }
    pub(super) fn observe(&self) -> FastCutoffResult {
        let admitted = ordinary_policy::fast_cutoff_gate(self.score,self.target-self.ply,
            self.upper,self.checked,self.previous_checked,self.capture.exception());
        let mut cutoff = None;
        let pressure_checked = admitted.is_some();
        let mut threat_queried = false;
        if let Some(adjusted) = admitted {
            if !self.pressure.guard() {
                threat_queried = true;
                let result = adjusted-self.threat;
                if result >= self.upper { cutoff = Some(result); }
            }
        }
        FastCutoffResult { score:cutoff,pressure_checked,threat_queried }
    }
}

pub(super) fn dispatch(operation: &str, input: &Value) -> Result<Value> {
    if operation == "evaluation.materialBalance" {
        let (root, position) = material(input)?;
        return Ok(json!({"score":root.material(&position)}));
    }
    if operation == "search.squareCaptureDefense" {
        object(input, &["placement", "squares"])?;
        let position = positions::placement(&input["placement"], true)?;
        let influence = Influence::build(&position);
        let mut defended = Vec::new();
        for square in array(&input["squares"], 1, 1024)? {
            defended.push(quiescence_policy::destination_support(
                &position,
                &influence,
                positions::square(square)?,
            ));
        }
        return Ok(json!({"defended":defended, "chargedRelationQueries":0}));
    }
    object(input, &["queries"])?;
    let maximum = match operation {
        "search.captureDefense" => 1024,
        "search.quiescenceCaptureAllowance" | "search.frontierEstimate" => 512,
        _ => 4096,
    };
    let mut results = Vec::new();
    for query in array(&input["queries"], 1, maximum)? {
        results.push(match operation {
            "search.captureException" => json!(capture_exception(query)?),
            "search.captureDefense" => {
                object(query, &["occupant", "white", "black"])?;
                let mut position = bare();
                let victim = match text(&query["occupant"])? {
                    "white" => Piece::new(Color::White, PieceKind::Pawn),
                    "black" => Piece::new(Color::Black, PieceKind::Pawn),
                    "empty" => Piece::EMPTY,
                    _ => return Err("invalid occupant color".into()),
                };
                position.board[DESTINATION.0 as usize] = victim;
                let mut influence = Influence { profiles: [[0; 64]; 2] };
                for (side, name) in moves::COLORS.iter().enumerate() {
                    influence.profiles[side][DESTINATION.0 as usize] = relations::profile(&query[*name])?;
                }
                json!(quiescence_policy::destination_support(&position, &influence, DESTINATION))
            }
            "search.quiescenceCaptureAllowance" => {
                object(query, &["material", "captured", "passedPawnContribution", "positionalContribution"])?;
                let (root, mut position) = material(&query["material"])?;
                capture(&mut position, &query["captured"], true)?;
                json!(quiescence_policy::allowance(&root, &position, &Move::new(SOURCE, DESTINATION, MoveKind::Ordinary),
                      integer(&query["positionalContribution"], -10000, 10000)?,
                      integer(&query["passedPawnContribution"], -10000, 10000)?))
            }
            "search.frontierEstimate" => {
                object(query, &["material", "sideToMove", "moveKind", "givesCheck", "captured", "staticScore", "passedPawnContribution", "positionalContribution"])?;
                let (root, mut position) = material(&query["material"])?;
                position.side = color(&query["sideToMove"])?;
                let victim = capture(&mut position, &query["captured"], false)?;
                if !victim.is_empty() && victim.color() == position.side {
                    return Err("frontier victim cannot be friendly".into());
                }
                let kind = match text(&query["moveKind"])? {
                    "ordinary" => MoveKind::Ordinary,
                    "promotion" => MoveKind::Promotion(PieceKind::Queen),
                    "enPassant" => MoveKind::EnPassant,
                    "castle" => MoveKind::Castle,
                    _ => return Err("invalid frontier move class".into()),
                };
                json!(ordinary_policy::frontier_estimate(&position, &root, Move::new(SOURCE, DESTINATION, kind),
                    boolean(&query["givesCheck"])?, integer(&query["staticScore"], -30000, 30000)?,
                    integer(&query["positionalContribution"], -10000, 10000)?,
                    integer(&query["passedPawnContribution"], -10000, 10000)?))
            }
            "search.kingPressure" => {
                let pressure = Pressure::parse(query)?;
                json!({"guard":pressure.guard(), "previousPressure":pressure.previous_pressure,
                       "currentPressure":pressure.current_pressure})
            }
            "search.fastCutoff" => FastCutoff::parse(query)?.observe().output(),
            _ => return Err(format!("unsupported supplied-context operation: {operation}")),
        });
    }
    let key = match operation {
        "search.captureException" => "exceptions",
        "search.captureDefense" => "defended",
        "search.quiescenceCaptureAllowance" => "allowances",
        "search.frontierEstimate" => "estimates",
        _ => "results",
    };
    let mut output = serde_json::Map::new();
    output.insert(key.into(), json!(results));
    if operation == "search.captureDefense" {
        output.insert("chargedRelationQueries".into(), json!(0));
    }
    Ok(Value::Object(output))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn empty_counts() -> Value {
        let counts = json!({"pawn":0,"knight":0,"bishop":0,"rook":0,"queen":0});
        json!({"white":counts,"black":counts})
    }

    #[test]
    fn independent_destination_facts_do_not_impose_board_consistency() {
        let q = json!({"promotion":null,"destination":{"side":"black","piece":"king"},"material":empty_counts()});
        assert_eq!(
            dispatch("search.captureException", &json!({"queries":[q]})).unwrap()["exceptions"],
            json!([true])
        );
        let mut crowded = empty_counts();
        crowded["white"]["knight"] = json!(15);
        crowded["black"]["rook"] = json!(15);
        assert!(counts(&crowded).is_ok());
        crowded["black"]["pawn"] = json!(1);
        assert!(counts(&crowded).is_err());
    }

    #[test]
    fn empty_capture_still_validates_both_profile_schemas() {
        let profile = json!({"weak":0,"queen":0,"rook":0,"minor":0,"pawn":0});
        let mut q = json!({"occupant":"empty","white":profile,"black":profile});
        assert_eq!(
            dispatch("search.captureDefense", &json!({"queries":[q.clone()]})).unwrap()["defended"],
            json!([false])
        );
        q["black"]["pawn"] = json!(32);
        assert!(dispatch("search.captureDefense", &json!({"queries":[q]})).is_err());
    }

    #[test]
    fn excluded_pressure_observations_remain_visible_without_entering_guard() {
        let profile = json!({"weak":0,"queen":0,"rook":0,"minor":0,"pawn":0});
        let mut neighbor = json!({"included":false,"previous":profile,"current":profile});
        neighbor["current"]["pawn"] = json!(3);
        let mut q = json!({"side":"black","neighbors":vec![neighbor;8]});
        let out = dispatch("search.kingPressure", &json!({"queries":[q.clone()]})).unwrap();
        assert_eq!(out["results"][0]["guard"], false);
        assert_eq!(out["results"][0]["currentPressure"], json!(vec![3; 8]));
        q["neighbors"][3]["included"] = json!(true);
        assert_eq!(
            dispatch("search.kingPressure", &json!({"queries":[q]})).unwrap()["results"][0]
                ["guard"],
            true
        );
    }
}
