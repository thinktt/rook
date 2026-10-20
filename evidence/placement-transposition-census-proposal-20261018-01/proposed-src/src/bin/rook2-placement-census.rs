//! D=true logging-only placement census. Ordinary wire behavior is retained.
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
    for option in std::env::args().skip(1) {
        match option.as_str() {
            "--diagnostic-seed-command" => diagnostic_seed = true,
            "--work-clock=kingwcr" => {}
            "--work-clock-post=work" => fine_work = true,
            _ => {
                return Err(Failure::Message(format!(
                    "rook2: unsupported option: {option}\n"
                )))
            }
        }
    }
    let mut input = Input::stdin()?;
    let mut output = io::stdout().lock();
    let mut errors = io::stderr().lock();
    let mut session = Session::<true>::default();
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
            Action::Quit => return Ok(()),
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
    Ok(())
}

fn main() -> ExitCode {
    if let Err(error) = rook2::placement_census::initialize() {
        let _ = writeln!(io::stderr(), "census initialize: {error}");
        return ExitCode::from(1);
    }
    let result = run();
    if let Err(error) = rook2::placement_census::finish() {
        let _ = writeln!(io::stderr(), "census finish: {error}");
        return ExitCode::from(1);
    }
    match result {
        Ok(()) => ExitCode::SUCCESS,
        Err(Failure::Fatal) => ExitCode::from(1),
        Err(Failure::Message(message)) => {
            let _ = io::stderr().write_all(message.as_bytes());
            ExitCode::from(1)
        }
    }
}
