//! Root scheduling, retry and ranking shared by actual and controlled searches.
//!
//! An identity is a slot in the caller's immutable initial candidate table. The
//! caller supplies actual absolute search work and executes each returned attempt;
//! this owner never fabricates a child answer or charges work itself.
use crate::timed::{aspiration, ranking_score};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Row {
    pub id: u16,
    pub score: i32,
    pub work: u64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Policy {
    Unrestricted,
    Restricted,
}

pub const fn policy(search_count: u64) -> Policy {
    if search_count >= 25000 {
        Policy::Restricted
    } else {
        Policy::Unrestricted
    }
}

/// The first candidate stays pinned; equal-effort tail rows keep their order.
pub fn order_tail(rows: &mut [Row], selected: Policy) {
    if selected == Policy::Restricted && rows.len() > 1 {
        rows[1..].sort_by_key(|row| std::cmp::Reverse(row.work));
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Attempt {
    pub id: u16,
    pub index: usize,
    pub window: [i32; 2],
    pub retry: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Completed {
    pub id: u16,
    pub index: usize,
    pub window: [i32; 2],
    pub returned_score: i32,
    pub score: i32,
    pub best: i32,
    pub second: i32,
    pub best_changed: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Returned {
    Retry(Attempt),
    Completed(Completed),
}

#[derive(Clone, Copy)]
struct Pending {
    attempt: Attempt,
    original_window: [i32; 2],
    before_search: u64,
}

/// One iteration owns the existing exploration and completed-ranking vectors.
/// Drop an interrupted instance without returning a score for its pending pass.
pub struct Iteration {
    rows: Vec<Row>,
    ranked: Vec<Row>,
    policy: Policy,
    previous: i32,
    best: i32,
    index: usize,
    pending: Option<Pending>,
}

impl Iteration {
    pub fn new(rows: Vec<Row>, search_count: u64, previous: i32) -> Self {
        assert!(!rows.is_empty());
        let ranked = Vec::with_capacity(rows.len());
        Self {
            rows,
            ranked,
            policy: policy(search_count),
            previous,
            best: -10000,
            index: 0,
            pending: None,
        }
    }

    pub fn policy(&self) -> Policy {
        self.policy
    }
    pub fn best(&self) -> i32 {
        self.best
    }
    pub fn second(&self) -> i32 {
        self.ranked.get(1).map_or(-10000, |r| r.score)
    }
    pub fn ranked(&self) -> &[Row] {
        &self.ranked
    }

    /// Begin a new candidate. A retry is returned only by `returned`, so a
    /// caller cannot accidentally reset the candidate's work origin between passes.
    pub fn next(&mut self, search_count: u64) -> Option<Attempt> {
        assert!(
            self.pending.is_none(),
            "pending root attempt must return first"
        );
        if self.index == self.rows.len() {
            return None;
        }
        if self.index == 1 {
            order_tail(&mut self.rows, self.policy);
        }
        let window = if self.policy == Policy::Restricted && self.index != 0 {
            aspiration(self.best, self.previous)
        } else {
            [self.second(), 10000]
        };
        let attempt = Attempt {
            id: self.rows[self.index].id,
            index: self.index,
            window,
            retry: false,
        };
        self.pending = Some(Pending {
            attempt,
            original_window: window,
            before_search: search_count,
        });
        Some(attempt)
    }

    /// Commit one normally returned adjusted root score. An interrupted child
    /// never calls this operation. Work includes both executed passes exactly once.
    pub fn returned(&mut self, returned_score: i32, search_count: u64) -> Returned {
        let mut pending = self.pending.take().expect("no pending root attempt");
        assert!(search_count >= pending.before_search);
        let restricted_nonfirst = self.policy == Policy::Restricted && self.index != 0;
        if restricted_nonfirst
            && !pending.attempt.retry
            && returned_score >= pending.original_window[1]
        {
            pending.attempt.retry = true;
            pending.attempt.window[1] = 10000;
            self.pending = Some(pending);
            return Returned::Retry(pending.attempt);
        }
        let score = ranking_score(returned_score, pending.original_window, restricted_nonfirst);
        let row = &mut self.rows[self.index];
        row.work += search_count - pending.before_search;
        row.score = score;
        let place = self.ranked.partition_point(|r| r.score >= score);
        self.ranked.insert(place, *row);
        let best_changed = score > self.best;
        if best_changed {
            self.best = score;
        }
        let completed = Completed {
            id: row.id,
            index: self.index,
            window: pending.original_window,
            returned_score,
            score,
            best: self.best,
            second: self.second(),
            best_changed,
        };
        self.index += 1;
        Returned::Completed(completed)
    }

    /// Carry only the completed stable ranking into the next iteration.
    pub fn into_ranked(self) -> Vec<Row> {
        assert!(self.pending.is_none() && self.index == self.rows.len());
        self.ranked
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn rows(work: &[u64]) -> Vec<Row> {
        work.iter()
            .enumerate()
            .map(|(id, &work)| Row {
                id: id as u16,
                score: 123,
                work,
            })
            .collect()
    }
    fn complete(value: Returned) -> Completed {
        match value {
            Returned::Completed(value) => value,
            _ => panic!("unexpected retry"),
        }
    }

    #[test]
    fn policy_is_frozen_and_tail_order_waits_for_first_completion() {
        let mut unrestricted = Iteration::new(rows(&[1, 3, 9, 9]), 24999, 0);
        assert_eq!(unrestricted.next(24999).unwrap().id, 0);
        complete(unrestricted.returned(5, 25001));
        assert_eq!(unrestricted.next(25001).unwrap().id, 1);
        assert_eq!(unrestricted.policy(), Policy::Unrestricted);
        let mut restricted = Iteration::new(rows(&[1, 3, 9, 9]), 25000, 0);
        assert_eq!(restricted.next(25000).unwrap().id, 0);
        assert_eq!(
            restricted.rows.iter().map(|r| r.id).collect::<Vec<_>>(),
            [0, 1, 2, 3]
        );
        complete(restricted.returned(5, 25002));
        assert_eq!(restricted.next(25002).unwrap().id, 2);
        assert_eq!(
            restricted.rows.iter().map(|r| r.id).collect::<Vec<_>>(),
            [0, 2, 3, 1]
        );
    }

    #[test]
    fn retry_retains_original_window_identity_and_both_passes_work() {
        let mut owner = Iteration::new(rows(&[100, 200]), 25000, 10);
        let first = owner.next(25000).unwrap();
        assert_eq!(first.window, [-10000, 10000]);
        let first = complete(owner.returned(10, 25003));
        assert!(first.best_changed);
        let next = owner.next(25003).unwrap();
        assert_eq!((next.id, next.window, next.retry), (1, [12, 13], false));
        let retry = match owner.returned(13, 25007) {
            Returned::Retry(attempt) => attempt,
            _ => panic!("expected retry"),
        };
        assert_eq!(
            (retry.id, retry.index, retry.window, retry.retry),
            (1, 1, [12, 10000], true)
        );
        let result = complete(owner.returned(12, 25012));
        assert_eq!(
            (result.window, result.returned_score, result.score),
            ([12, 13], 12, 10)
        );
        assert!(!result.best_changed);
        assert_eq!((result.best, result.second), (10, 10));
        assert!(owner.next(25012).is_none());
        let ranked = owner.into_ranked();
        assert_eq!(
            ranked.iter().map(|r| (r.id, r.work)).collect::<Vec<_>>(),
            [(0, 103), (1, 209)]
        );
    }

    #[test]
    fn sentinel_ties_do_not_invent_a_best_and_high_identity_survives() {
        let mut initial = rows(&[0, 0]);
        initial[1].id = 511;
        let mut owner = Iteration::new(initial, 0, 0);
        assert_eq!(owner.next(0).unwrap().id, 0);
        assert!(!complete(owner.returned(-10000, 1)).best_changed);
        assert_eq!(owner.next(1).unwrap().id, 511);
        let last = complete(owner.returned(-10000, 2));
        assert!(!last.best_changed);
        assert_eq!((last.best, last.second), (-10000, -10000));
        assert_eq!(
            owner.into_ranked().iter().map(|r| r.id).collect::<Vec<_>>(),
            [0, 511]
        );
    }
}


/// Controlled root-relative reply; it is not a real child or a production charge.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SuppliedReply {
    pub score: i32,
    pub work: u64,
}

/// Indexed by immutable original slot, never by a reordered exploration index.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SuppliedCandidate {
    pub prior_work: u64,
    pub first: SuppliedReply,
    pub retry: Option<SuppliedReply>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SuppliedPass {
    pub attempt: Attempt,
    pub returned_score: i32,
    pub search_count: u64,
}

pub struct SuppliedStep {
    pub completed: Completed,
    pub passes: Vec<SuppliedPass>,
    pub ranked: Vec<Row>,
}
impl SuppliedStep {
    /// A projection of the produced prefix, not an extra scheduler state field.
    pub fn insertion_rank(&self) -> usize {
        self.ranked.iter().position(|row| row.id == self.completed.id)
            .expect("completed identity missing from produced prefix")
    }
}

pub struct SuppliedOutcome {
    pub steps: Vec<SuppliedStep>,
    pub search_count: u64,
    pub ranked: Vec<Row>,
}

/// Execute one bounded supplied-reply iteration through the actual native owner.
/// Callers validate identities/domains before entry; all executed work sums and
/// per-candidate carried work must fit u64. No diagnostic 2^53 policy is imposed
/// on production scheduling or this native arithmetic. A missing retry is valid
/// only if the actual owner never requests it. This driver owns count additions,
/// attempted reply selection, pass chronology and produced-prefix snapshots.
/// It does not generate chess positions, add relation charges or run time checks.
pub fn supplied_iteration(
    initial_search_count: u64,
    previous_best: i32,
    supplied: &[SuppliedCandidate],
) -> SuppliedOutcome {
    assert!(!supplied.is_empty() && supplied.len() <= usize::from(u16::MAX) + 1);
    let rows = supplied.iter().enumerate().map(|(id, candidate)| Row {
        id: id as u16, score: 0, work: candidate.prior_work,
    }).collect();
    let mut owner = Iteration::new(rows, initial_search_count, previous_best);
    let mut search_count = initial_search_count;
    let mut steps = Vec::with_capacity(supplied.len());
    while let Some(mut attempt) = owner.next(search_count) {
        let mut passes = Vec::with_capacity(2);
        loop {
            let candidate = supplied[usize::from(attempt.id)];
            let reply = if attempt.retry {
                candidate.retry.expect("actual root owner requested an absent supplied retry")
            } else { candidate.first };
            search_count = search_count.checked_add(reply.work)
                .expect("supplied absolute search count exceeds u64");
            passes.push(SuppliedPass { attempt, returned_score: reply.score, search_count });
            match owner.returned(reply.score, search_count) {
                Returned::Retry(next) => attempt = next,
                Returned::Completed(completed) => {
                    steps.push(SuppliedStep { completed, passes, ranked: owner.ranked().to_vec() });
                    break;
                }
            }
        }
    }
    SuppliedOutcome { steps, search_count, ranked: owner.into_ranked() }
}

#[cfg(test)]
mod supplied_tests {
    use super::*;
    fn candidate(prior_work:u64,score:i32,work:u64,retry:Option<(i32,u64)>)->SuppliedCandidate {
        SuppliedCandidate { prior_work,first:SuppliedReply{score,work},
            retry:retry.map(|(score,work)|SuppliedReply{score,work}) }
    }
    #[test]
    fn supplied_unrestricted_crossing_keeps_prefix_ties_and_native_u64_domain() {
        let out=supplied_iteration(24999,0,&[
            candidate(0,10,2,None),candidate(2,10,0,None),candidate(50,5,0,None)]);
        assert_eq!(out.search_count,25001);
        assert_eq!(out.steps.iter().map(|s|s.completed.id).collect::<Vec<_>>(),[0,1,2]);
        assert_eq!(out.steps.iter().map(|s|s.completed.window).collect::<Vec<_>>(),
            [[-10000,10000],[-10000,10000],[10,10000]]);
        assert_eq!(out.steps.iter().map(SuppliedStep::insertion_rank).collect::<Vec<_>>(),[0,1,2]);
        assert!(out.steps.iter().all(|s|s.passes.len()==1));
        let mut next=out.ranked;order_tail(&mut next,policy(out.search_count));
        assert_eq!(next.iter().map(|r|(r.id,r.work)).collect::<Vec<_>>(),[(0,2),(2,50),(1,2)]);
        // Exact-interchange limits belong only to the cold JSON admission.
        let above_safe=9_007_199_254_740_992;
        let out=supplied_iteration(above_safe,0,&[candidate(above_safe,10000,1,Some((-10000,999)))]);
        assert_eq!(out.search_count,above_safe+1);assert_eq!(out.ranked[0].work,above_safe+1);
        assert_eq!(out.steps[0].passes.len(),1);
    }
    #[test]
    fn supplied_restricted_reordering_keeps_reply_ownership_and_ignores_unused_work() {
        let out=supplied_iteration(25000,10,&[
            candidate(100,10,3,Some((10000,999))),
            candidate(200,-5,4,Some((10000,888))),
            candidate(300,13,5,Some((12,7)))]);
        assert_eq!(out.steps.iter().map(|s|s.completed.id).collect::<Vec<_>>(),[0,2,1]);
        assert_eq!(out.steps.iter().map(|s|s.passes.len()).collect::<Vec<_>>(),[1,2,1]);
        assert_eq!(out.steps[1].passes.iter().map(|p|(p.attempt.window,p.returned_score,p.search_count))
            .collect::<Vec<_>>(),[([12,13],13,25008),([12,10000],12,25015)]);
        assert_eq!((out.steps[1].completed.returned_score,out.steps[1].completed.score),(12,10));
        assert_eq!(out.steps[1].insertion_rank(),1);
        assert_eq!(out.search_count,25019);
        assert_eq!(out.ranked.iter().map(|r|(r.id,r.score,r.work)).collect::<Vec<_>>(),
            [(0,10,103),(2,10,312),(1,-7,204)]);
    }
}
