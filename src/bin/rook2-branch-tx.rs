//! Isolated fixed-completion/NoHost branch-transaction pilot; not a wire engine.
use rook2::{branch_transactions::{self, Caps}, engine::Config,
    evaluator::Parameters, history::SearchHistory,
    movegen::{self,MoveList}, position::Position};

fn run() -> Result<(),String> {
    let mut args=std::env::args().skip(1);
    let mut input=None;
    let mut caps=Caps {max_depth:8,max_tail_candidates:8,queue_depth:2,log_events:16384};
    while let Some(key)=args.next() {
        let value=args.next().ok_or("missing option value")?;
        match key.as_str() {
            "--input"=>input=Some(value),
            "--queue-depth"=>caps.queue_depth=value.parse().map_err(|_|"bad queue depth")?,
            "--max-depth"=>caps.max_depth=value.parse().map_err(|_|"bad maximum depth")?,
            "--max-tail"=>caps.max_tail_candidates=value.parse().map_err(|_|"bad tail cap")?,
            "--log-events"=>caps.log_events=value.parse().map_err(|_|"bad log cap")?,
            _=>return Err(format!("unknown option {key}")),
        }
    }
    let text=std::fs::read_to_string(input.ok_or("--input required")?).map_err(|e|e.to_string())?;
    let mut fen=None;let mut moves=None;let mut own=None;let mut opponent=None;
    let mut evaluation=None;let mut search=None;let mut randomness=None;
    for line in text.lines() {
        if line.is_empty() || line.starts_with('#') {continue;}
        let (key,value)=line.split_once('=').ok_or("bad input assignment")?;
        match key {
            "case"=>{},
            "fen"=>fen=Some(value.to_string()),
            "moves"=>moves=Some(value.to_string()),
            "own"=>own=Some(value.to_string()),
            "opponent"=>opponent=Some(value.to_string()),
            "evaluation"=>evaluation=Some(value.to_string()),
            "search"=>search=Some(value.to_string()),
            "randomness"=>randomness=Some(value.parse::<i32>().map_err(|_|"bad randomness")?),
            _=>return Err(format!("unknown input key {key}")),
        }
    }
    // These released profiling inputs use rnd=0; no claim is made about root
    // seed adjustments or live Host/Clock behavior in this research adapter.
    if randomness!=Some(0) {return Err("branch pilot admits only explicit zero randomness".into());}
    fn numbers<const N:usize>(s:Option<String>)->Result<[i32;N],String> {
        let values:Vec<i32>=s.ok_or("missing numerical input")?.split(',')
            .map(|x|x.parse().map_err(|_|"bad numerical input".to_string())).collect::<Result<_,_>>()?;
        values.try_into().map_err(|_|"wrong numerical input arity".into())
    }
    let eval=numbers::<3>(evaluation)?;
    let parameters=Parameters {own:numbers(own)?,opponent:numbers(opponent)?,
        average_depth:eval[0],draw:eval[1],opponent_selectivity:eval[2]};
    let setup=numbers::<4>(search)?;
    if setup[1]<1 || setup[2]<48 {return Err("invalid depth/table input".into());}
    let config=Config {selectivity:setup[0],maximum_depth:setup[1] as usize,
        tts_bytes:setup[2] as usize,analysis:setup[3]};
    let mut position=Position::from_fen(&fen.ok_or("missing initial FEN")?)?;
    let mut history=SearchHistory::new(&position);
    for token in moves.ok_or("missing moves")?.split_whitespace() {
        let mut legal=MoveList::new();movegen::generate_legal(&position,&mut legal);
        let movement=*legal.as_slice().iter().find(|m|m.to_string()==token)
            .ok_or_else(||format!("invalid history move {token}"))?;
        position=position.played_unchecked(movement);
        history.push(&position,Some(movement));
    }
    history.mark_root();
    let report=branch_transactions::run(position,history,parameters,config,caps)?;
    println!("{}",report.json());
    if report.unsafe_validation {return Err("semantic acceptance disagrees with canonical execution".into());}
    if report.controls.iter().any(|c| !c.passed) {return Err("transaction machinery control failed".into());}
    Ok(())
}

fn main() {
    if let Err(error)=run() {eprintln!("branch transaction pilot: {error}");std::process::exit(1);}
}
