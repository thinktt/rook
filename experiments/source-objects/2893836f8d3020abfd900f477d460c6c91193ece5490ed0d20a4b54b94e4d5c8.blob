//! Produced pre-root boundaries and the reversible search tail.
//!
//! Equality deliberately uses primary fingerprint, side, rights and EP only.
//! Placement, secondary identity and chronology must not strengthen that rule.

use crate::position::Position;
use crate::types::{Color, Move};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Boundary {
    pub primary: u32,
    pub side: Color,
    pub rights: u8,
    pub ep: u8,
    pub halfmove: u8,
}

impl From<&Position> for Boundary {
    fn from(position: &Position) -> Self {
        Self {
            primary: position.primary,
            side: position.side,
            rights: position.rights,
            ep: position.ep,
            halfmove: position.halfmove,
        }
    }
}

impl Boundary {
    fn same_repetition_state(self, earlier: Self) -> bool {
        self.primary == earlier.primary
            && self.side == earlier.side
            && self.rights == earlier.rights
            && self.ep == earlier.ep
    }
}

pub struct SearchHistory {
    boundaries: Vec<Boundary>,
    arrivals: Vec<Option<Move>>,
    root: usize,
}

impl SearchHistory {
    pub fn new(initial: &Position) -> Self {
        let mut boundaries = Vec::with_capacity(864);
        let mut arrivals = Vec::with_capacity(864);
        boundaries.push(Boundary::from(initial));
        arrivals.push(None);
        Self {
            boundaries,
            arrivals,
            root: 0,
        }
    }

    /// Append already produced game states before `mark_root`, or recursive
    /// children afterward. Null search transitions use `None` as arrival.
    pub fn push(&mut self, position: &Position, arrival: Option<Move>) {
        self.boundaries.push(Boundary::from(position));
        self.arrivals.push(arrival.filter(|m| *m != Move::NONE));
    }

    /// Freeze all available game history at its current root boundary.
    pub fn mark_root(&mut self) {
        self.root = self.boundaries.len() - 1;
    }

    pub fn reset_search(&mut self) {
        self.boundaries.truncate(self.root + 1);
        self.arrivals.truncate(self.root + 1);
    }

    pub fn pop(&mut self) {
        assert!(
            self.boundaries.len() > self.root + 1,
            "cannot remove pre-root history"
        );
        self.boundaries.pop();
        self.arrivals.pop();
    }

    pub fn search_ply(&self) -> usize {
        self.boundaries.len() - self.root - 1
    }
    pub fn pre_root_len(&self) -> usize {
        self.root
    }
    pub fn previous_move(&self) -> Option<Move> {
        *self.arrivals.last().unwrap()
    }

    pub fn repetition_count(&self, in_check: bool) -> u32 {
        let current = *self.boundaries.last().unwrap();
        let h = current.halfmove as usize;
        if h < 4 {
            return 0;
        }
        if h > 100 || (h == 100 && !in_check) {
            return 50;
        }
        let index = self.boundaries.len() - 1;
        let mut matches = 0;
        for distance in (4..=h.min(index)).step_by(2) {
            matches += u32::from(current.same_repetition_state(self.boundaries[index - distance]));
        }
        if matches == 0 {
            0
        } else {
            matches + 1
        }
    }

    pub fn short_reversal(&self) -> bool {
        let p = self.search_ply();
        let index = self.boundaries.len() - 1;
        let current = self.boundaries[index];
        if p < 3 || current.halfmove < 3 {
            return false;
        }
        let (Some(m), Some(e)) = (self.arrivals[index], self.arrivals[index - 2]) else {
            return false;
        };
        let baseline = self.boundaries[index - 3];
        m.from() == e.to()
            && m.to() == e.from()
            && current.rights == baseline.rights
            && current.ep == baseline.ep
    }
}

pub fn repetition_draw(count: u32, search_ply: usize, ana: i32) -> bool {
    count > 0 && (ana == 0 || search_ply >= 3 || count >= 3)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::movegen::{generate_legal, MoveList};
    use crate::types::{MoveKind, Square};
    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

    fn mv(from: &str, to: &str) -> Move {
        Move::new(
            Square::parse(from).unwrap(),
            Square::parse(to).unwrap(),
            MoveKind::Ordinary,
        )
    }

    #[test]
    fn actual_cycles_cross_root_boundary_and_restore_only_search_tail() {
        let mut position = Position::from_fen(START).unwrap();
        let mut history = SearchHistory::new(&position);
        let cycle = [
            mv("g1", "f3"),
            mv("g8", "f6"),
            mv("f3", "g1"),
            mv("f6", "g8"),
        ];
        for (index, movement) in cycle.into_iter().cycle().take(8).enumerate() {
            let mut legal = MoveList::new();
            generate_legal(&position, &mut legal);
            assert!(legal.as_slice().contains(&movement));
            position = position.played_unchecked(movement);
            history.push(&position, Some(movement));
            if index == 1 {
                history.mark_root();
            }
            if index == 3 {
                assert_eq!(history.repetition_count(false), 2);
            }
        }
        assert_eq!(history.repetition_count(false), 3);
        assert_eq!(history.pre_root_len(), 2);
        history.reset_search();
        assert_eq!(history.search_ply(), 0);
        assert_eq!(history.previous_move(), Some(cycle[1]));
    }

    #[test]
    fn distance_two_and_secondary_geometry_do_not_change_equality() {
        let mut position = Position::from_fen(START).unwrap();
        let mut history = SearchHistory::new(&position);
        for _ in 0..2 {
            position.halfmove += 1;
            history.push(&position, None);
        }
        assert_eq!(history.repetition_count(false), 0);
        for _ in 0..2 {
            position.halfmove += 1;
            history.push(&position, None);
        }
        position.secondary ^= 123;
        assert_eq!(history.repetition_count(false), 2);
        history.pop();
        position.ep = 20;
        history.push(&position, None);
        assert_eq!(history.repetition_count(false), 0);
    }

    #[test]
    fn halfmove_hundred_check_exception_preserves_numeric_count() {
        for (h, check, expected) in [
            (3, false, 0),
            (100, false, 50),
            (100, true, 0),
            (101, true, 50),
            (255, false, 50),
        ] {
            let mut position = Position::from_fen(START).unwrap();
            position.halfmove = h;
            assert_eq!(
                SearchHistory::new(&position).repetition_count(check),
                expected
            );
        }
        assert!(!repetition_draw(2, 1, -1));
        assert!(!repetition_draw(2, 2, 1));
        assert!(repetition_draw(2, 3, 1));
        assert!(repetition_draw(3, 1, -1));
        assert!(repetition_draw(2, 1, 0));
    }

    #[test]
    fn reversal_uses_endpoints_and_flags_but_not_side_or_null_equality() {
        let mut position = Position::from_fen(START).unwrap();
        let mut history = SearchHistory::new(&position);
        for movement in [Some(mv("g1", "f3")), None, Some(mv("f3", "g1"))] {
            position.halfmove += 1;
            history.push(&position, movement);
        }
        assert!(history.short_reversal());
        history.pop();
        history.push(&position, None);
        assert!(!history.short_reversal());
        history.pop();
        position.rights = 0;
        history.push(&position, Some(mv("f3", "g1")));
        assert!(!history.short_reversal());
    }
}
