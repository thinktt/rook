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

fn thread_request(value: &str) -> Result<usize, Failure> {
    value.parse::<usize>().ok().filter(|&value| value > 0)
        .ok_or_else(|| Failure::Message("rook2: --threads requires a positive integer\n".into()))
}

fn run() -> Result<(), Failure> {
    let mut diagnostic_seed = false;
    let mut fine_work = false;
    let mut requested_threads = 1;
    let mut inspect_threads = false;
    #[cfg(feature = "child-preparation")]
    let mut child_budget = None;
    for option in std::env::args().skip(1) {
        match option.as_str() {
            "--diagnostic-seed-command" => diagnostic_seed = true,
            "--work-clock=kingwcr" => {}
            "--work-clock-post=work" => fine_work = true,
            #[cfg(feature = "child-preparation")]
            "--child-preparation=1" => child_budget=Some(1),
            #[cfg(feature = "child-preparation")]
            "--child-preparation=2" => child_budget=Some(2),
            #[cfg(feature = "child-preparation")]
            "--child-preparation=4" => child_budget=Some(4),
            "--inspect-threads" => inspect_threads = true,
            _ if option.starts_with("--threads=") => {
                requested_threads = thread_request(&option["--threads=".len()..])?;
            }
            _ => {
                return Err(Failure::Message(format!(
                    "rook2: unsupported option: {option}\n"
                )))
            }
        }
    }
    // Disable development counters and root traces in the ordinary binary.
    let mut session = Session::<false>::default();
    session.set_threads(requested_threads)
        .map_err(|message| Failure::Message(format!("rook2: {message}\n")))?;
    #[cfg(feature = "child-preparation")]
    if let Some(budget)=child_budget {session.set_child_preparation_budget(budget)
        .map_err(|message|Failure::Message(message))?;}
    if inspect_threads {
        let requested = session.requested_threads().map_err(Failure::Message)?;
        let configured = session.configured_threads().map_err(Failure::Message)?;
        println!("{{\"requested_threads\":{requested},\"configured_threads\":{configured}}}");
        return Ok(());
    }
    let mut input = Input::stdin()?;
    let mut output = io::stdout().lock();
    let mut errors = io::stderr().lock();
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

#[cfg(test)]
mod tests {
    use super::thread_request;

    #[test]
    fn thread_argument_requires_a_positive_representable_integer() {
        for value in ["1","2","3"] {assert_eq!(thread_request(value).ok(),value.parse::<usize>().ok());}
        assert_eq!(thread_request(&usize::MAX.to_string()).ok(),Some(usize::MAX));
        for value in ["","0","-1","1.5","abc"," 2","184467440737095516160"] {
            assert!(thread_request(value).is_err(),"accepted {value:?}");
        }
    }
}
