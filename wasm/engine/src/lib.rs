//! Persistent ordinary engine; all search and session semantics live in rook2.
#[path = "../../abi.rs"]
mod abi;
use rook2::{host::{Host, Record}, quiescence::Limits, session::{Action, Error, Session}, wire};
use std::io;

pub struct Engine { session: Session<false>, diagnostic_seed: bool, fine_work: bool }
struct BrowserHost { seed: Option<u32>, diagnostic_seed: bool }
impl Host for BrowserHost {
    fn acquire_seed(&mut self, _supplied: u32, entry: u32) -> io::Result<u32> {
        Ok(self.seed.unwrap_or_else(|| rook2::host::seed_from_seconds(abi::seconds(), entry)))
    }
    fn started(&mut self, seed: u32) -> io::Result<()> {
        if self.diagnostic_seed { abi::emit(2, &format!("KING_SEARCH_SEED seed={seed}\n")); }
        Ok(())
    }
    fn command(&mut self) -> io::Result<Option<rook2::host::Command>> {
        abi::poll()?.map(|line| wire::search_command(&line)).transpose()
    }
    fn publish(&mut self, record: Record) -> io::Result<()> {
        abi::emit(1, &record.wire()); Ok(())
    }
}
impl Engine {
    fn command(&mut self, line: &str) -> Result<u32, Error> {
        if self.diagnostic_seed {
            if let Some(seed) = wire::seed_assignment(line) {
                match seed {
                    Ok(seed) => {
                        self.session.seed_override = Some(seed);
                        abi::emit(1, &format!("king_seed {seed}\n"));
                        return Ok(0);
                    }
                    Err(()) => {
                        abi::emit(2, "king-native: invalid diagnostic seed command\n");
                        return Ok(1);
                    }
                }
            }
        }
        match self.session.idle(line)? {
            Action::Quit => return Ok(2),
            Action::Reply(lines) => for line in lines { abi::emit(1, &line); },
            Action::Search => {
                let host = BrowserHost { seed: self.session.seed_override, diagnostic_seed: self.diagnostic_seed };
                self.session.go_live(host, 0, Limits::default(), 62, self.fine_work).0?;
            }
        }
        Ok(0)
    }
}

// flags: bit0 diagnostic seed command, bit1 fine-work posts.
#[no_mangle]
pub extern "C" fn rook_create(flags: u32) -> *mut Engine {
    Box::into_raw(Box::new(Engine { session: Session::default(), diagnostic_seed: flags & 1 != 0, fine_work: flags & 2 != 0 }))
}
#[no_mangle]
pub unsafe extern "C" fn rook_destroy(engine: *mut Engine) { drop(Box::from_raw(engine)); }
// 0=continue, 1=fatal, 2=quit. No reentrant calls on an engine handle.
#[no_mangle]
pub unsafe extern "C" fn rook_command(engine: *mut Engine, pointer: *const u8, length: usize) -> u32 {
    match (*engine).command(abi::text(pointer, length)) {
        Ok(status) => status,
        Err(Error::FatalEmptyRoot | Error::FatalKingVictim) => 1,
        Err(error) => { abi::emit(2, &format!("rook2: {error:?}\n")); 1 }
    }
}
