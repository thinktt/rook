//! Cold public result formatting; stored PVs and charged work are untouched.
use crate::movegen::{generate_legal, in_check, MoveList};
use crate::ordinary_policy::selective_depth;
use crate::position::Position;
use crate::timed::{Capture, Outcome};
use crate::types::{Move, MoveKind, PieceKind};

pub fn reported_score(ranking: i32, draw: i32) -> i32 {
    if ranking <= -9000 || ranking >= 9000 {
        ranking
    } else {
        (ranking as i64 - draw as i64).clamp(-7900, 7900) as i32
    }
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Fields {
    pub depth_token: i32,
    pub evaluation: i32,
    pub centiseconds: i32,
    pub search_id: u64,
}

impl Fields {
    pub fn prefix(self) -> String {
        format!(
            "{:>5} {:+5} {:>6} {:>9}",
            self.depth_token, self.evaluation, self.centiseconds, self.search_id
        )
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Post {
    pub fields: Fields,
    /// Raw King line, without LF; castles retain digit zero.
    pub line: String,
    /// Displayed semantic move text, with letter-O castles.
    pub pv: String,
    pub displayed_moves: usize,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct InvalidPv {
    pub index: usize,
    pub movement: Move,
}

fn letter(kind: PieceKind) -> char {
    match kind {
        PieceKind::Pawn => 'P',
        PieceKind::Knight => 'N',
        PieceKind::Bishop => 'B',
        PieceKind::Rook => 'R',
        PieceKind::Queen => 'Q',
        PieceKind::King => 'K',
    }
}

/// Format one legal token and return its produced position for the next token.
pub fn token(position: &Position, movement: Move) -> Option<(String, Position)> {
    let mut legal = MoveList::new();
    generate_legal(position, &mut legal);
    if !legal.as_slice().contains(&movement) {
        return None;
    }
    let piece = position.board[movement.from().0 as usize];
    let kind = piece.kind();
    let capture = movement.kind() == MoveKind::EnPassant
        || !position.board[movement.to().0 as usize].is_empty();
    let mut text = String::with_capacity(8);
    if movement.kind() == MoveKind::Castle {
        text.push_str(if movement.to().file() > movement.from().file() {
            "0-0"
        } else {
            "0-0-0"
        });
    } else {
        if kind != PieceKind::Pawn {
            text.push(letter(kind));
            let (mut alternative, mut same_file, mut same_rank) = (false, false, false);
            for &other in legal.as_slice() {
                if other != movement
                    && other.to() == movement.to()
                    && position.board[other.from().0 as usize] == piece
                {
                    alternative = true;
                    same_file |= other.from().file() == movement.from().file();
                    same_rank |= other.from().rank() == movement.from().rank();
                }
            }
            if alternative {
                let file_unique = !same_file;
                let rank_unique = !same_rank;
                if file_unique || !rank_unique {
                    text.push((b'a' + movement.from().file()) as char);
                }
                if !file_unique {
                    text.push((b'1' + movement.from().rank()) as char);
                }
            }
        } else if capture {
            text.push((b'a' + movement.from().file()) as char);
        }
        if capture {
            text.push('x');
        }
        text.push_str(&movement.to().to_string());
        if let MoveKind::Promotion(promoted) = movement.kind() {
            text.push(letter(promoted));
        }
    }
    let next = position.played_unchecked(movement);
    if in_check(&next, next.side) {
        text.push('+');
    }
    Some((text, next))
}

/// Preformatted token seam sharing the append-then-test boundary with real PVs.
pub fn displayed_tokens(prefix_length: usize, tokens: &[String]) -> (Vec<String>, usize) {
    let mut length = prefix_length;
    let mut included = Vec::new();
    for token in tokens {
        length += 1 + token.len();
        included.push(token.clone());
        if length > 380 {
            break;
        }
    }
    (included, length)
}

pub fn render(mut position: Position, pv: &[Move], fields: Fields) -> Result<Post, InvalidPv> {
    let mut line = fields.prefix();
    let mut semantic = String::new();
    let mut displayed_moves = 0;
    for (index, &movement) in pv.iter().enumerate() {
        let (text, next) = token(&position, movement).ok_or(InvalidPv { index, movement })?;
        line.push(' ');
        line.push_str(&text);
        if displayed_moves != 0 {
            semantic.push(' ');
        }
        semantic.push_str(&text.replace('0', "O"));
        position = next;
        displayed_moves += 1;
        if line.len() > 380 {
            break;
        }
    }
    Ok(Post {
        fields,
        line,
        pv: semantic,
        displayed_moves,
    })
}

pub fn capture_fields(root: &Position, capture: &Capture, draw: i32, selectivity: i32) -> Fields {
    let depth = capture.depth as i32;
    let margin = selective_depth(depth, selectivity, root.phase().endgame, depth).margin;
    Fields {
        depth_token: 1000 * depth + margin,
        evaluation: reported_score(capture.score, draw),
        centiseconds: capture.elapsed_cs as i32,
        search_id: capture.search_id,
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Event {
    Post(Post),
    Move(Move),
}

impl Event {
    pub fn wire(&self) -> String {
        match self {
            Self::Post(post) => format!("{}\n", post.line),
            Self::Move(m) => format!("move {m}\n"),
        }
    }
}

/// Native completed-search projection. Live publication/toggles belong to the session caller.
pub fn completed_events(
    root: Position,
    outcome: &Outcome,
    draw: i32,
    selectivity: i32,
    post_enabled: bool,
) -> Result<Vec<Event>, InvalidPv> {
    let selected = outcome
        .result
        .as_ref()
        .and_then(|r| r.pv.first())
        .copied()
        .unwrap_or(outcome.initial_candidates[0]);
    let mut events = Vec::new();
    if post_enabled {
        if !outcome.publications.is_empty() {
            for capture in &outcome.publications {
                events.push(Event::Post(render(
                    root,
                    &capture.pv,
                    capture_fields(&root, capture, draw, selectivity),
                )?));
            }
        } else if let Some(capture) = &outcome.result {
            events.push(Event::Post(render(
                root,
                &capture.pv,
                capture_fields(&root, capture, draw, selectivity),
            )?));
        } else {
            events.push(Event::Post(render(root, &[selected], Fields::default())?));
        }
    }
    events.push(Event::Move(selected));
    Ok(events)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::Square;
    fn movement(from: &str, to: &str) -> Move {
        Move::new(
            Square::parse(from).unwrap(),
            Square::parse(to).unwrap(),
            MoveKind::Ordinary,
        )
    }

    #[test]
    fn legal_disambiguation_filters_pins_and_distinguishes_file_rank_and_both() {
        for (fen, from, to, expected) in [
            ("7k/8/8/8/8/8/8/KN3N2 w - - 0 1", "b1", "d2", "Nbd2"),
            ("7k/8/8/1N6/8/8/8/KN6 w - - 0 1", "b1", "c3", "N1c3"),
            ("7k/8/8/8/8/1N6/8/KN3N2 w - - 0 1", "b1", "d2", "Nb1d2"),
            ("4r2k/8/8/8/8/8/2N1N3/4K3 w - - 0 1", "c2", "d4", "Nd4"),
        ] {
            let p = Position::from_fen(fen).unwrap();
            assert_eq!(token(&p, movement(from, to)).unwrap().0, expected);
        }
    }

    #[test]
    fn numeric_widths_signs_and_raw_castling_survive_wire_rendering() {
        let p = Position::from_fen("4k3/8/8/8/8/8/8/4K2R w K - 0 1").unwrap();
        let m = Move::new(
            Square::parse("e1").unwrap(),
            Square::parse("g1").unwrap(),
            MoveKind::Castle,
        );
        let post = render(
            p,
            &[m],
            Fields {
                depth_token: 3001,
                evaluation: 0,
                centiseconds: 0,
                search_id: 7,
            },
        )
        .unwrap();
        assert_eq!(post.line, " 3001    +0      0         7 0-0");
        assert_eq!(post.pv, "O-O");
        assert_eq!(
            Event::Post(post).wire(),
            " 3001    +0      0         7 0-0\n"
        );
    }

    #[test]
    fn crossing_token_is_retained_and_an_invalid_suffix_is_never_consumed() {
        let p = Position::from_fen("q1q4k/8/q7/4p3/4P3/Q7/8/Q1Q4K w - - 0 1").unwrap();
        let cycle = [
            movement("a1", "c3"),
            movement("a8", "c6"),
            movement("c3", "a1"),
            movement("c6", "a8"),
        ];
        let mut pv: Vec<Move> = cycle.into_iter().cycle().take(63).collect();
        pv[59] = Move::NONE;
        let post = render(p, &pv, Fields::default()).unwrap();
        assert_eq!(post.displayed_moves, 59);
        assert_eq!(post.line.len(), 382);
        assert!(post.line.ends_with("Qc3a1"));
        assert_eq!(pv[59], Move::NONE);
    }
}
