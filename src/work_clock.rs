//! Observed work ledger. Search owns N/R; observations own the carried origin.
use crate::quiescence::Work;


/// One native charged search unit. Limits precede increment; a due poll follows
/// the credited unit. Starting from zero, non-overflowing counts never poll at0.
pub(crate) fn charge_search_unit(units:&mut u64,limit:Option<u64>)
    ->Result<bool,crate::quiescence::Stopped> {
    if let Some(limit)=limit {
        if *units>=limit {return Err(crate::quiescence::Stopped::NodeLimit(limit));}
    }
    *units+=1;
    Ok(*units&4095==0)
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Ledger {
    origin: u32,
    last: u32,
    numerator: u128,
}

impl Ledger {
    pub fn with_origin(origin: u32) -> Self {
        Self {
            origin,
            last: origin,
            numerator: 0,
        }
    }

    pub fn observe(&mut self, work: Work) -> u32 {
        self.numerator = 3806 * work.effective_search_count() as u128
            + 770 * work.charged_relation_queries as u128;
        let increment = (self.numerator / 30_000_000).min(i32::MAX as u128) as u32;
        self.last = self.origin.wrapping_add(increment);
        self.last
    }

    /// Carry only the most recent observation; the caller clears its segment work.
    pub fn reset(&mut self) {
        self.origin = self.last;
        self.numerator = 0;
    }

    pub fn last(&self) -> u32 {
        self.last
    }

    pub fn fine_post(&self) -> i32 {
        (self.numerator / 1000).min(i32::MAX as u128) as i32
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn shared_unit_admission_credits_poll_boundary_and_refuses_limit_before_increment() {
        let mut units=4095;
        assert_eq!(charge_search_unit(&mut units,Some(4096)),Ok(true));assert_eq!(units,4096);
        assert_eq!(charge_search_unit(&mut units,Some(4096)),Err(crate::quiescence::Stopped::NodeLimit(4096)));
        assert_eq!(units,4096);
        let mut zero=0;
        assert_eq!(charge_search_unit(&mut zero,Some(0)),Err(crate::quiescence::Stopped::NodeLimit(0)));
        assert_eq!(zero,0);assert_eq!(charge_search_unit(&mut zero,None),Ok(false));assert_eq!(zero,1);
    }

    #[test]
    fn fine_snapshot_belongs_to_observation_and_reset_discards_segment_fraction() {
        let mut clock = Ledger::with_origin(u32::MAX);
        let just_under = Work {
            charged_search_units: 7882,
            charged_relation_queries: 0,
        };
        assert_eq!(clock.observe(just_under), u32::MAX);
        assert_eq!(clock.fine_post(), 29998);
        clock.reset();
        assert_eq!(clock.fine_post(), 0);
        assert_eq!(clock.observe(just_under), u32::MAX);
        let over = Work {
            charged_relation_queries: 2,
            ..just_under
        };
        assert_eq!(clock.observe(over), 0);
        assert_eq!(clock.fine_post(), 30000);
        clock.reset();
        assert_eq!(clock.fine_post(), 0);
        assert_eq!(clock.observe(Work::default()), 0);
    }
}
