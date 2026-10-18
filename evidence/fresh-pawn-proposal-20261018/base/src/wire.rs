//! Cold Linux byte-record input and ordinary search-time command parsing.
//!
//! Input is nonblocking only while a search polls it. Idle waits use poll(2),
//! without a reader thread or work on another measurement CPU.
use crate::host::Command;
use crate::parameters;
use std::fs::File;
use std::io::{self, Read};
use std::os::fd::{AsRawFd, FromRawFd};

const F_GETFL: i32 = 3;
const F_SETFL: i32 = 4;
const O_NONBLOCK: i32 = 0o4000;
const POLLIN: i16 = 1;

#[repr(C)]
struct PollFd {
    fd: i32,
    events: i16,
    revents: i16,
}

extern "C" {
    fn dup(fd: i32) -> i32;
    fn fcntl(fd: i32, command: i32, ...) -> i32;
    fn poll(fds: *mut PollFd, count: usize, timeout_ms: i32) -> i32;
}

fn invalid(message: &'static str) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidInput, message)
}

pub struct Input {
    file: File,
    original_flags: i32,
    buffer: Vec<u8>,
    consumed: usize,
    eof: bool,
}
impl Input {
    pub fn stdin() -> io::Result<Self> {
        // dup returns a new owned descriptor. Dropping Input never closes fd 0.
        let fd = unsafe { dup(0) };
        if fd < 0 {
            return Err(io::Error::last_os_error());
        }
        // This descriptor is owned exclusively by the new File.
        Self::new(unsafe { File::from_raw_fd(fd) })
    }

    pub fn new(file: File) -> io::Result<Self> {
        let fd = file.as_raw_fd();
        // The live File owns this valid descriptor throughout both calls.
        let original_flags = unsafe { fcntl(fd, F_GETFL) };
        if original_flags < 0 || unsafe { fcntl(fd, F_SETFL, original_flags | O_NONBLOCK) } < 0 {
            return Err(io::Error::last_os_error());
        }
        Ok(Self {
            file,
            original_flags,
            buffer: Vec::with_capacity(4096),
            consumed: 0,
            eof: false,
        })
    }

    /// Consume at most one complete available record. EOF is never a search command.
    pub fn try_line(&mut self) -> io::Result<Option<String>> {
        loop {
            let remaining = &self.buffer[self.consumed..];
            if let Some(end) = remaining.iter().position(|&b| b == b'\n') {
                if end + 1 > 1023 {
                    return Err(invalid("overlength command record"));
                }
                let payload = remaining[..end]
                    .strip_suffix(b"\r")
                    .unwrap_or(&remaining[..end]);
                if !payload.is_ascii() || payload.iter().any(|&b| b == 0 || b == b'\r') {
                    return Err(invalid("invalid command record"));
                }
                let line = String::from_utf8(payload.to_vec()).unwrap();
                if line.split([' ', '\t']).filter(|s| !s.is_empty()).count() > 40 {
                    return Err(invalid("too many command tokens"));
                }
                self.consumed += end + 1;
                return Ok(Some(line));
            }
            if remaining.len() >= 1023 {
                return Err(invalid("overlength command record"));
            }
            if self.eof {
                return if remaining.is_empty() {
                    Ok(None)
                } else {
                    Err(invalid("unterminated final command record"))
                };
            }
            if self.consumed != 0 {
                self.buffer.drain(..self.consumed);
                self.consumed = 0;
            }
            let mut chunk = [0; 4096];
            match self.file.read(&mut chunk) {
                Ok(0) => self.eof = true,
                Ok(n) => self.buffer.extend_from_slice(&chunk[..n]),
                Err(e) if e.kind() == io::ErrorKind::Interrupted => {}
                Err(e) if e.kind() == io::ErrorKind::WouldBlock => return Ok(None),
                Err(e) => return Err(e),
            }
        }
    }

    pub fn line(&mut self) -> io::Result<Option<String>> {
        loop {
            let line = self.try_line()?;
            if line.is_some() || self.eof {
                return Ok(line);
            }
            let mut fd = PollFd {
                fd: self.file.as_raw_fd(),
                events: POLLIN,
                revents: 0,
            };
            // fd points to one initialized pollfd for the duration of the call.
            if unsafe { poll(&mut fd, 1, -1) } < 0 {
                let error = io::Error::last_os_error();
                if error.kind() != io::ErrorKind::Interrupted {
                    return Err(error);
                }
            }
        }
    }
}
impl Drop for Input {
    fn drop(&mut self) {
        // Restore the open-file flags shared with the original stdin descriptor.
        unsafe { fcntl(self.file.as_raw_fd(), F_SETFL, self.original_flags) };
    }
}

/// None denotes an ordinary unknown command, including a bare keyword.
pub fn seed_assignment(line: &str) -> Option<Result<u32, ()>> {
    let rest = line
        .trim_start_matches([' ', '\t'])
        .strip_prefix("king_seed")?;
    if !rest.starts_with([' ', '\t']) {
        return None;
    }
    let mut words = rest.split([' ', '\t']).filter(|s| !s.is_empty());
    let Some(value) = words.next() else {
        return Some(Err(()));
    };
    if words.next().is_some() {
        return Some(Err(()));
    }
    Some(seed_value(value))
}

fn seed_value(text: &str) -> Result<u32, ()> {
    let negative = text.starts_with('-');
    let text = text.strip_prefix(['+', '-']).unwrap_or(text);
    let (radix, digits) =
        if let Some(hex) = text.strip_prefix("0x").or_else(|| text.strip_prefix("0X")) {
            (16, hex)
        } else if text.starts_with('0') {
            (8, text)
        } else {
            (10, text)
        };
    if digits.is_empty() {
        return Err(());
    }
    let mut value = 0u32;
    for byte in digits.bytes() {
        let digit = match byte {
            b'0'..=b'9' => (byte - b'0') as u32,
            b'a'..=b'f' => (byte - b'a' + 10) as u32,
            b'A'..=b'F' => (byte - b'A' + 10) as u32,
            _ => return Err(()),
        };
        if digit >= radix {
            return Err(());
        }
        value = value
            .checked_mul(radix)
            .and_then(|v| v.checked_add(digit))
            .ok_or(())?;
    }
    if negative && value != 0 {
        Err(())
    } else {
        Ok(value)
    }
}

pub fn search_command(line: &str) -> io::Result<Command> {
    let words: Vec<&str> = line.split([' ', '\t']).filter(|s| !s.is_empty()).collect();
    Ok(match words.as_slice() {
        ["?"] => Command::Finish,
        ["force"] => Command::Abort,
        ["."] => Command::Status,
        ["post"] => Command::Post(true),
        ["nopost"] => Command::Post(false),
        ["easy"] => Command::Easy,
        ["time", value] => {
            Command::Time(parameters::integer(value).map_err(|_| invalid("invalid time"))?)
        }
        ["otim", value] => {
            parameters::integer(value).map_err(|_| invalid("invalid opponent time"))?;
            Command::Ignore
        }
        [] => Command::Ignore,
        _ => return Err(invalid("unsupported command during search")),
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use std::os::fd::OwnedFd;
    use std::os::unix::net::UnixStream;

    fn pair() -> (Input, UnixStream) {
        let (reader, writer) = UnixStream::pair().unwrap();
        let file = File::from(OwnedFd::from(reader));
        (Input::new(file).unwrap(), writer)
    }

    #[test]
    fn split_records_wait_without_consuming_a_partial_line() {
        let (mut input, mut writer) = pair();
        writer.write_all(b".\nfor").unwrap();
        assert_eq!(input.try_line().unwrap().as_deref(), Some("."));
        assert_eq!(input.try_line().unwrap(), None);
        writer.write_all(b"ce\r\n?\n").unwrap();
        assert_eq!(input.try_line().unwrap().as_deref(), Some("force"));
        assert_eq!(input.try_line().unwrap().as_deref(), Some("?"));
        drop(writer);
        assert_eq!(input.line().unwrap(), None);
    }

    #[test]
    fn record_limit_counts_crlf_and_preserves_the_last_payload_byte() {
        for (length, ending, valid) in [
            (1022, "\n", true),
            (1021, "\r\n", true),
            (1022, "\r\n", false),
            (1023, "\n", false),
        ] {
            let (mut input, mut writer) = pair();
            writer
                .write_all(format!("{}{ending}", "a".repeat(length)).as_bytes())
                .unwrap();
            let result = input.line();
            assert_eq!(result.is_ok(), valid, "{length} {ending:?}");
            if valid {
                assert_eq!(result.unwrap().unwrap().len(), length);
            }
        }
        for bytes in [&b"abc"[..], b"a\rb\n", b"a\0b\n", b"\xff\n"] {
            let (mut input, mut writer) = pair();
            writer.write_all(bytes).unwrap();
            drop(writer);
            assert!(input.line().is_err());
        }
    }

    #[test]
    fn seed_lexical_domain_and_keyword_boundary() {
        for (text, value) in [
            ("0", 0),
            ("-0x00", 0),
            ("+0377", 255),
            ("4294967295", u32::MAX),
            ("0Xffffffff", u32::MAX),
        ] {
            assert_eq!(
                seed_assignment(&format!("\tking_seed\t{text} \t")),
                Some(Ok(value))
            );
        }
        for text in ["", "+", "--0", "-1", "08", "0x", "4294967296", "1 2", "1.0"] {
            assert_eq!(seed_assignment(&format!("king_seed {text}")), Some(Err(())));
        }
        for text in ["king_seed", "king_seeds 1", "king_seed=1"] {
            assert_eq!(seed_assignment(text), None);
        }
    }
}
