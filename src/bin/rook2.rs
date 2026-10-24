//! Ordinary King XBoard wire profile. No diagnostic JSON is accepted here.
use rook2::host::{Command, Host, Record};
use rook2::quiescence::Limits;
use rook2::session::{Action, Error, Session};
use rook2::wire::{self, Input};
use std::io::{self, Write};
use std::process::ExitCode;
use std::time::{SystemTime, UNIX_EPOCH};

struct WireHost<'a, W, E> {
    input: &'a mut Input,
    output: &'a mut W,
    errors: &'a mut E,
    seed_override: Option<u32>,
    diagnostic_seed: bool,
}
impl<W: Write, E: Write> Host for WireHost<'_, W, E> {
    fn acquire_seed(&mut self, _supplied: u32, entry: u32) -> io::Result<u32> {
        if let Some(seed) = self.seed_override {
            return Ok(seed);
        }
        let seconds = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map_err(io::Error::other)?
            .as_secs() as u32;
        Ok(rook2::host::seed_from_seconds(seconds, entry))
    }
    fn started(&mut self, seed: u32) -> io::Result<()> {
        if self.diagnostic_seed {
            writeln!(self.errors, "KING_SEARCH_SEED seed={seed}")?;
            self.errors.flush()?;
        }
        Ok(())
    }
    fn command(&mut self) -> io::Result<Option<Command>> {
        self.input
            .try_line()?
            .map(|line| wire::search_command(&line))
            .transpose()
    }
    fn publish(&mut self, record: Record) -> io::Result<()> {
        self.output.write_all(record.wire().as_bytes())?;
        self.output.flush()
    }
}

enum Failure {
    Fatal,
    Message(String),
}
impl From<io::Error> for Failure {
    fn from(error: io::Error) -> Self {
        Self::Message(format!("rook2: {error}\n"))
    }
}
impl From<Error> for Failure {
    fn from(error: Error) -> Self {
        match error {
            Error::FatalEmptyRoot | Error::FatalKingVictim => Self::Fatal,
            e => Self::Message(format!("rook2: {e:?}\n")),
        }
    }
}

fn run() -> Result<(), Failure> {
    let mut diagnostic_seed = false;
    let mut fine_work = false;
    let mut research_threads = 1;
    let mut explicit_threads = false;
    let mut research_full = None;
    #[cfg(feature = "inventory-census")]
    let mut inventory_census = false;
    #[cfg(feature = "child-preparation")]
    let mut child_budget = None;
    for option in std::env::args().skip(1) {
        match option.as_str() {
            "--diagnostic-seed-command" => diagnostic_seed = true,
            "--work-clock=kingwcr" => {}
            "--work-clock-post=work" => fine_work = true,
            #[cfg(feature = "inventory-census")]
            "--inventory-census" => inventory_census = true,
            #[cfg(feature = "child-preparation")]
            "--child-preparation=1" => child_budget=Some(1),
            #[cfg(feature = "child-preparation")]
            "--child-preparation=2" => child_budget=Some(2),
            #[cfg(feature = "child-preparation")]
            "--child-preparation=4" => child_budget=Some(4),
            "--research-threads=1" => {research_threads = 1; explicit_threads = true;},
            "--research-threads=2" => {research_threads = 2; explicit_threads = true;},
            "--research-full=inline" => research_full = Some(rook2::evaluator::ResearchFullMode::Inline),
            "--research-full=current" => research_full = Some(rook2::evaluator::ResearchFullMode::Current),
            "--research-full=reversed" => research_full = Some(rook2::evaluator::ResearchFullMode::Reversed),
            "--research-full=inventory" => research_full = Some(rook2::evaluator::ResearchFullMode::Inventory),
            _ => {
                return Err(Failure::Message(format!(
                    "rook2: unsupported option: {option}\n"
                )))
            }
        }
    }
    if research_full.is_some() && explicit_threads {
        return Err(Failure::Message("rook2: --research-full and --research-threads are mutually exclusive\n".into()));
    }
    #[cfg(feature = "child-preparation")]
    if research_full.is_some() && child_budget.is_some() {
        return Err(Failure::Message("rook2: --research-full and --child-preparation are mutually exclusive\n".into()));
    }
    #[cfg(feature = "inventory-census")]
    let inventory_report = if inventory_census {
        if research_threads != 1 || research_full.is_some_and(|mode|
            mode != rook2::evaluator::ResearchFullMode::Inline) {
            return Err(Failure::Message("rook2: inventory census requires inline evaluation\n".into()));
        }
        #[cfg(feature = "child-preparation")]
        if child_budget.is_some() {
            return Err(Failure::Message("rook2: inventory census cannot enable child preparation\n".into()));
        }
        let path = std::env::var_os("ROOK2_INVENTORY_CENSUS_REPORT").ok_or_else(||
            Failure::Message("rook2: inventory census requires ROOK2_INVENTORY_CENSUS_REPORT\n".into()))?;
        if std::path::Path::new(&path).exists() {
            return Err(Failure::Message("rook2: inventory census report must be a fresh path\n".into()));
        }
        rook2::inventory_census::enable().map_err(Failure::Message)?;
        Some(path)
    } else {None};
    let inventory_worker_report = std::env::var_os("ROOK2_INVENTORY_WORKER_REPORT");
    if inventory_worker_report.as_ref().is_some_and(|path|std::path::Path::new(path).exists()) {
        return Err(Failure::Message("rook2: inventory worker report must be a fresh path\n".into()));
    }
    let mut input = Input::stdin()?;
    let mut output = io::stdout().lock();
    let mut errors = io::stderr().lock();
    // Disable development counters and root traces in the ordinary binary.
    let mut session = Session::<false>::default();
    (if let Some(mode) = research_full {session.set_research_full_mode(mode)}
        else {session.set_research_thread_budget(research_threads)})
        .map_err(|message| Failure::Message(format!("rook2: {message}\n")))?;
    #[cfg(feature = "child-preparation")]
    if let Some(budget)=child_budget {session.set_child_preparation_budget(budget)
        .map_err(|message|Failure::Message(message))?;}
    while let Some(line) = input.line()? {
        if diagnostic_seed {
            if let Some(assignment) = wire::seed_assignment(&line) {
                let value = assignment.map_err(|_| {
                    Failure::Message("king-native: invalid diagnostic seed command\n".into())
                })?;
                session.seed_override = Some(value);
                writeln!(output, "king_seed {value}")?;
                output.flush()?;
                continue;
            }
        }
        match session.idle(&line)? {
            Action::Quit => break,
            Action::Reply(replies) => {
                for reply in replies {
                    output.write_all(reply.as_bytes())?;
                }
                output.flush()?;
            }
            Action::Search => {
                let host = WireHost {
                    input: &mut input,
                    output: &mut output,
                    errors: &mut errors,
                    seed_override: session.seed_override,
                    diagnostic_seed,
                };
                let (result, _) = session.go_live(host, 0, Limits::default(), 62, fine_work);
                result?;
            }
        }
    }
    #[cfg(feature = "child-preparation")]
    if child_budget.is_some() {
        let stats=session.finish_child_preparation().map_err(Failure::Message)?;
        if let Some(path)=std::env::var_os("ROOK2_CHILD_PREPARATION_REPORT") {
            let mut file=std::fs::OpenOptions::new().write(true).create_new(true).open(path)?;
            writeln!(file,"{stats}")?;
        } else {writeln!(errors,"CHILD_PREPARATION_STATS {stats}")?;}
    }
    #[cfg(feature = "inventory-census")]
    if let Some(path) = inventory_report {
        let report = rook2::inventory_census::finish_json().map_err(Failure::Message)?;
        let mut file = std::fs::OpenOptions::new().write(true).create_new(true).open(path)?;
        writeln!(file,"{report}")?;
    }
    if let Some(path) = inventory_worker_report {
        let report = session.finish_inventory_worker().map_err(Failure::Message)?;
        let mut file = std::fs::OpenOptions::new().write(true).create_new(true).open(path)?;
        writeln!(file,"{report}")?;
    }
    Ok(())
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(Failure::Fatal) => ExitCode::from(1),
        Err(Failure::Message(message)) => {
            let _ = io::stderr().write_all(message.as_bytes());
            ExitCode::from(1)
        }
    }
}
