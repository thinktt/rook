//! Ordered public parameter storage, kept outside recursive search state.
use crate::engine::{Config, Search};
use crate::evaluator::Parameters as Evaluation;

pub const NAMES: [&str; 30] = [
    "myp", "opp", "myn", "opn", "myb", "opb", "myr", "opr", "myq", "opq", "myk", "opk", "mycc",
    "opcc", "mymob", "opmob", "myks", "opks", "mypp", "oppp", "mypw", "oppw", "avd", "sop", "rnd",
    "sel", "cfd", "md", "ana", "tts",
];

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Parameters {
    pub values: [i32; 30],
}

impl Default for Parameters {
    fn default() -> Self {
        let mut values = [100; 30];
        for index in [10, 11, 22, 24, 26, 28] {
            values[index] = 0;
        }
        values[25] = 14;
        values[27] = 999;
        values[29] = 75497472;
        Self { values }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Error {
    Name,
    Integer,
    EffectiveDomain,
}

pub fn integer(text: &str) -> Result<i32, Error> {
    let bytes = text.as_bytes();
    let digits = if matches!(bytes.first(), Some(b'+') | Some(b'-')) {
        &bytes[1..]
    } else {
        bytes
    };
    if digits.is_empty() || !digits.iter().all(u8::is_ascii_digit) {
        return Err(Error::Integer);
    }
    text.parse().map_err(|_| Error::Integer)
}

impl Parameters {
    fn selection(name: &str) -> Option<(usize, Option<usize>)> {
        match name {
            "cc" => Some((12, Some(13))),
            "mob" => Some((14, Some(15))),
            "ks" => Some((16, Some(17))),
            "pp" => Some((18, Some(19))),
            "pw" => Some((20, Some(21))),
            _ => NAMES.iter().position(|&n| n == name).map(|i| (i, None)),
        }
    }
    pub fn get(&self, name: &str) -> Option<i32> {
        Self::selection(name).map(|(i, _)| self.values[i])
    }
    pub fn command(&mut self, args: &[&str]) -> Result<String, Error> {
        let mut response = String::from("cm_parm");
        for &arg in args {
            response.push(' ');
            if arg == "default" {
                let inert = self.values[11];
                *self = Self::default();
                self.values[11] = inert;
                response.push_str("default");
                continue;
            }
            let (name, assignment) = arg
                .split_once('=')
                .map_or((arg, None), |(n, v)| (n, Some(v)));
            let mut bytes = name.bytes();
            if !bytes.next().is_some_and(|b| b.is_ascii_alphabetic())
                || !bytes.all(|b| b.is_ascii_alphanumeric() || b == b'_')
            {
                return Err(Error::Name);
            }
            let assignment = assignment.map(integer).transpose()?;
            response.push_str(name);
            response.push('=');
            if let Some((own, other)) = Self::selection(name) {
                if let Some(value) = assignment {
                    self.values[own] = value;
                    if let Some(other) = other {
                        self.values[other] = value;
                    }
                }
                response.push_str(&self.values[own].to_string());
            } else {
                response.push('?');
            }
        }
        Ok(response)
    }

    /// Bind effective native domains. The stored opk is excluded from all admission.
    pub fn bind<const D: bool>(&self, search: &mut Search<D>) -> Result<(), Error> {
        let v = self.values;
        if !(0..22)
            .filter(|&i| i != 11)
            .all(|i| (0..=1000).contains(&v[i]))
            || !(-100..=100).contains(&v[22])
            || !(0..=100).contains(&v[23])
            || v[24] < 0
            || !(-10000..=10000).contains(&v[26])
            || !(1..=999).contains(&v[27])
            || v[28] < 0
            || v[29] < 96
        {
            return Err(Error::EffectiveDomain);
        }
        search.evaluator.parameters = Evaluation {
            own: std::array::from_fn(|i| v[2 * i]),
            opponent: std::array::from_fn(|i| v[2 * i + 1]),
            average_depth: v[22],
            draw: v[26],
            opponent_selectivity: v[23],
        };
        search.config = Config {
            selectivity: v[25],
            maximum_depth: v[27] as usize,
            analysis: v[28],
            tts_bytes: v[29] as usize,
        };
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{history::SearchHistory, position::Position, quiescence::Limits, timed::Controls};
    #[test]
    fn every_stored_opk_is_excluded_from_real_search_admission_and_behavior() {
        let p =
            Position::from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1").unwrap();
        let mut baseline = None;
        for opk in [0, i32::MIN, i32::MAX] {
            let mut params = Parameters::default();
            params.values[11] = opk;
            params.values[29] = 65536;
            let mut search = Search::<false>::new(&p);
            params.bind(&mut search).unwrap();
            let mut history = SearchHistory::new(&p);
            let out = search
                .run_work_timed(
                    p,
                    &mut history,
                    Controls {
                        average_cs: 1,
                        maximum_cs: 1,
                        origin: 0,
                        seed: 0,
                        randomness: 50,
                        maximum_entered_iterations: 6,
                    },
                    Limits::default(),
                )
                .unwrap();
            let events = crate::output::completed_events(
                p,
                &out,
                search.evaluator.draw_preference,
                search.config.selectivity,
                true,
            )
            .unwrap();
            let observed = (out.result, out.stop, events);
            if let Some(ref before) = baseline {
                assert_eq!(before, &observed);
            } else {
                baseline = Some(observed);
            }
            assert_eq!(history.search_ply(), 0);
        }
    }
}
