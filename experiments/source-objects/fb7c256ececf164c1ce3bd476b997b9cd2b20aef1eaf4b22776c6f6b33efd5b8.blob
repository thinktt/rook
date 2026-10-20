//! Adaptive ordinary allowances and the completed-iteration terminal decision.
use crate::ordinary_policy::selective_depth;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Stage {
    BestChange,
    ScoreDrop,
    Root,
    Iteration,
    EasyIteration,
    Poll,
}

#[derive(Clone, Debug)]
pub struct Adaptive {
    pub limits: [f64; 3],
    pub changes: [u32; 3],
    pub clock_reads: u64,
    pub start: u32,
    average: f64,
    checked: bool,
    depth: i32,
}

impl Adaptive {
    /// `start` is the initialization observation already obtained by the caller.
    pub fn new(average_cs: u32, maximum_cs: u32, checked: bool, start: u32) -> Self {
        let average = average_cs as f64 * 0.01;
        let limits = [
            if average_cs == 0 {
                999000000.0
            } else {
                average * if checked { 0.29 } else { 0.52 }
            },
            if average_cs == 0 {
                999000000.0
            } else {
                average * if checked { 0.47 } else { 0.85 }
            },
            if maximum_cs == 0 {
                999000000.0
            } else {
                maximum_cs as f64 * 0.01
            },
        ];
        Self {
            limits,
            changes: [0; 3],
            clock_reads: 1,
            start,
            average,
            checked,
            depth: 0,
        }
    }

    pub fn elapsed_cs(&self, clock: u32) -> u32 {
        clock.wrapping_sub(self.start)
    }

    pub fn apply<F: FnMut() -> u32>(
        &mut self,
        stage: Stage,
        depth: i32,
        previous: i32,
        best: i32,
        second: i32,
        mut observe: F,
    ) -> bool {
        if depth > self.depth {
            self.changes = [0, self.changes[0], self.changes[1]];
            self.depth = depth;
        }
        if stage == Stage::BestChange {
            self.changes[0] += 1;
            if depth <= 3 {
                return false;
            }
        }
        if stage == Stage::EasyIteration && self.average != 0.0 {
            let margin = best.min(100) - second;
            let factor = if self.checked {
                if margin > 800 {
                    0.333
                } else if margin > 400 {
                    0.5
                } else if margin > 170 {
                    0.666
                } else {
                    1.0
                }
            } else if margin > 800 {
                0.25
            } else if margin > 400 {
                0.333
            } else if margin > 170 {
                0.5
            } else if margin > 70 {
                0.666
            } else {
                1.0
            };
            self.limits[0] *= factor;
            self.limits[1] *= factor;
        }
        if depth == 1 && matches!(stage, Stage::Root | Stage::Iteration | Stage::EasyIteration) {
            return false;
        }
        let clock = observe();
        self.clock_reads += 1;
        let elapsed = self.elapsed_cs(clock) as f64 * 0.01;
        match stage {
            Stage::BestChange => {
                if elapsed > self.limits[0] * 0.5 && self.limits[1] < self.average {
                    let instability = 3 * self.changes[0].min(3)
                        + 2 * self.changes[1].min(3)
                        + self.changes[2].min(3);
                    let factor = if instability > 14 {
                        2.0
                    } else if instability > 10 {
                        1.5
                    } else {
                        1.0
                    };
                    self.limits[0] *= factor;
                    self.limits[1] *= factor;
                }
                false
            }
            Stage::ScoreDrop => {
                if elapsed > self.limits[0] * 0.5 {
                    let units = previous / 100;
                    let threshold = 100 + 8 * (units * units).min(100);
                    let drop = previous - best;
                    if drop > threshold * 30 / 100 {
                        self.limits[1] *= 2.0;
                        if drop > threshold * 130 / 100 {
                            self.limits[1] *= 2.0;
                            self.limits[0] *= 2.0;
                        }
                    }
                }
                false
            }
            Stage::Root => elapsed >= self.limits[1],
            Stage::Iteration | Stage::EasyIteration => elapsed >= self.limits[0],
            Stage::Poll => elapsed >= self.limits[2],
        }
    }
}

pub struct Terminal {
    pub depth: i32,
    pub selectivity: i32,
    pub root_endgame: u16,
    pub maximum_depth: usize,
    pub analysis: i32,
    pub average_cs: u32,
    pub best: i32,
    pub second: i32,
    pub previous: i32,
    pub start: u32,
    pub clock: u32,
    pub iteration_limit: f64,
}

impl Terminal {
    pub fn mate_margin(&self) -> i32 {
        selective_depth(self.depth, self.selectivity, self.root_endgame, self.depth).margin
    }
    pub fn elapsed_cs(&self) -> i32 {
        self.clock.wrapping_sub(self.start) as i32
    }
    pub fn reason(&self) -> Option<&'static str> {
        let depth = self.depth;
        if depth > 1 && self.elapsed_cs() as f64 * 0.01 >= self.iteration_limit {
            Some("elapsed52")
        } else if self.average_cs != 0 && depth > 1 && self.best >= 9000 && self.previous >= 9000 {
            Some("confirmedWinningScore")
        } else if self.average_cs != 0 && depth > 1 && self.best <= -9000 {
            Some("losingBestScore")
        } else if self.average_cs != 0 && depth > 1 && self.second <= -9000 && self.analysis == 0 {
            Some("losingAlternativeScore")
        } else if depth > 61 {
            Some("iterationCeiling")
        } else if depth as usize >= self.maximum_depth {
            Some("personalityDepth")
        } else if self.best >= 10000 - self.mate_margin() {
            Some("winningMateBound")
        } else if self.best <= -10000 + self.mate_margin() {
            Some("losingMateBound")
        } else {
            None
        }
    }
}
