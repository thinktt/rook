//! Schedule allocation and the persistent game-clock adjustment.
use crate::time_powers::POWERS;
use crate::types::Color;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Stage {
    pub moves: u32,
    pub base_seconds: u32,
    pub increment_seconds: u32,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Schedule {
    pub stages: Vec<Stage>,
}

impl Default for Schedule {
    fn default() -> Self {
        Self {
            stages: vec![Stage {
                moves: 999,
                base_seconds: 300,
                increment_seconds: 0,
            }],
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Error {
    EmptySchedule,
    ZeroStage,
    ArithmeticDomain,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Allowance {
    pub move_index: u32,
    pub average_cs: u32,
    pub maximum_cs: u32,
}

impl Schedule {
    pub fn seconds(&self, mut index: u64) -> Result<u64, Error> {
        if self.stages.is_empty() {
            return Err(Error::EmptySchedule);
        }
        let mut total = 0u128;
        for (stage_index, stage) in self.stages.iter().enumerate() {
            if stage.moves == 0 {
                return Err(Error::ZeroStage);
            }
            let moves = stage.moves as u64;
            let full = stage.base_seconds as u128 + stage.increment_seconds as u128 * moves as u128;
            if stage_index + 1 == self.stages.len() {
                total += full * (index / moves) as u128;
                index %= moves;
            } else if index >= moves {
                total += full;
                index -= moves;
                continue;
            }
            total += stage.base_seconds as u128 + stage.increment_seconds as u128 * index as u128;
            return total.try_into().map_err(|_| Error::ArithmeticDomain);
        }
        unreachable!()
    }

    pub fn allowance(
        &self,
        game_ply: u32,
        adjustment_cs: i32,
        optimism: i32,
        pondering: bool,
    ) -> Result<Allowance, Error> {
        let index = game_ply / 2;
        let elapsed = adjustment_cs as f64 * 0.01;
        let planning = if pondering {
            27.0 + 0.15 * (100 - optimism) as f64
        } else {
            36.0 + 0.1 * (100 - optimism) as f64
        };
        let mut target = 999000000.0f64;
        for (j, &power) in POWERS.iter().enumerate() {
            let credit = self.seconds(index as u64 + j as u64)? as f64;
            let quotient = (credit - elapsed) / ((1.0 - 0.96 * power) * planning);
            target = target.min(quotient);
        }
        let budget = (self.seconds(index as u64)? as f64 - elapsed - 1.0)
            .min(0.75 * (self.seconds(index as u64 + 1)? as f64 - elapsed - 1.0))
            .min(0.6 * (self.seconds(index as u64 + 2)? as f64 - elapsed - 1.0));
        let average = target.max(0.5);
        let maximum = budget.max(1.0).min(4.0 * average);
        let convert = |seconds: f64| {
            let centiseconds = (100.0 * seconds).trunc();
            if !centiseconds.is_finite() || !(0.0..=i32::MAX as f64).contains(&centiseconds) {
                Err(Error::ArithmeticDomain)
            } else {
                Ok(centiseconds as u32)
            }
        };
        Ok(Allowance {
            move_index: index,
            average_cs: convert(average)?,
            maximum_cs: convert(maximum)?,
        })
    }
}

#[derive(Clone, Debug, Default)]
pub struct GameClock {
    pub schedule: Schedule,
    pub adjustment_cs: i32,
    start: Option<u32>,
}

impl GameClock {
    pub(crate) fn vacant() -> Self {
        Self {
            schedule: Schedule { stages: Vec::new() },
            adjustment_cs: 0,
            start: None,
        }
    }
    pub fn effective_adjustment(&self, now: u32) -> i32 {
        self.adjustment_cs
            .wrapping_add(self.start.map_or(0, |start| now.wrapping_sub(start) as i32))
    }
    pub fn begin(&mut self, now: u32) {
        assert!(self.start.is_none());
        self.start = Some(now);
    }
    pub fn finish(&mut self, now: u32) {
        self.adjustment_cs = self.effective_adjustment(now);
        self.start = None;
    }
    pub fn reset_adjustment(&mut self) {
        self.adjustment_cs = 0;
        self.start = None;
    }
    pub fn synchronize(
        &mut self,
        remaining_cs: i32,
        game_ply: u32,
        initial: Color,
        selected: Color,
        now: u32,
    ) -> Result<(), Error> {
        let index = (game_ply as u64 + u64::from(initial == selected)) / 2;
        let seconds = self.schedule.seconds(index)?;
        let credit = seconds.checked_mul(100).ok_or(Error::ArithmeticDomain)?;
        if credit > i32::MAX as u64 {
            return Err(Error::ArithmeticDomain);
        }
        let base = (credit as i32).wrapping_sub(remaining_cs);
        self.adjustment_cs =
            base.wrapping_sub(self.start.map_or(0, |start| now.wrapping_sub(start) as i32));
        Ok(())
    }
    pub fn allowance(
        &self,
        game_ply: u32,
        optimism: i32,
        pondering: bool,
        now: u32,
    ) -> Result<Allowance, Error> {
        self.schedule.allowance(
            game_ply,
            self.effective_adjustment(now),
            optimism,
            pondering,
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn active_synchronization_preserves_start_and_finishing_charges_later_observed_time() {
        let mut clock = GameClock::default();
        clock.begin(u32::MAX - 5);
        clock
            .synchronize(1000, 0, Color::White, Color::Black, 2)
            .unwrap();
        assert_eq!(clock.effective_adjustment(2), 29000);
        clock.finish(7);
        assert_eq!(clock.adjustment_cs, 29005);
        assert_eq!(clock.effective_adjustment(1000), 29005);
        clock.reset_adjustment();
        assert_eq!(clock.schedule, Schedule::default());
    }
}
