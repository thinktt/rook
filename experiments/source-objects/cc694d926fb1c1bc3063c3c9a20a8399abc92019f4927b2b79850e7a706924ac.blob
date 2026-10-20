//! Cold host events at actual root-capture and charged-work poll boundaries.
use crate::clock::GameClock;
use crate::output::{Post, Status};
use crate::session::GameResult;
use crate::types::{Color, Move};
use std::io;

/// Seed arithmetic shared by native session preparation and actual host acquisition.
/// Callers own the seconds sample and its existing timing/error boundary.
#[inline]
pub fn seed_from_seconds(seconds: u32, entry: u32) -> u32 {
    seconds.wrapping_add(entry)
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Command {
    Finish,
    Abort,
    Status,
    Post(bool),
    Time(i32),
    Ignore,
    Easy,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Record {
    Post(Post),
    Status(Status),
    Aborting,
    Move(Move),
    Result(GameResult),
}
impl Record {
    pub fn wire(&self) -> String {
        match self {
            Self::Post(p) => format!("{}\n", p.line),
            Self::Status(s) => format!("{}\n", s.line),
            Self::Aborting => "aborting search ...\n".to_owned(),
            Self::Move(m) => format!("move {m}\n"),
            Self::Result(r) => r.wire(),
        }
    }
}

pub trait Host {
    const ACTIVE: bool = true;
    fn acquire_seed(&mut self, supplied: u32, _entry: u32) -> io::Result<u32> {
        Ok(supplied)
    }
    fn started(&mut self, _seed: u32) -> io::Result<()> {
        Ok(())
    }
    fn command(&mut self) -> io::Result<Option<Command>> {
        Ok(None)
    }
    fn publish(&mut self, _record: Record) -> io::Result<()> {
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, Default)]
pub struct NoHost;
impl Host for NoHost {
    const ACTIVE: bool = false;
}

pub(crate) struct Control {
    pub clock: GameClock,
    pub post: bool,
    pub force: bool,
    pub pondering: bool,
    pub published: bool,
    pub fine_work: bool,
    pub game_ply: u32,
    pub initial_side: Color,
    pub clock_color: Color,
}
