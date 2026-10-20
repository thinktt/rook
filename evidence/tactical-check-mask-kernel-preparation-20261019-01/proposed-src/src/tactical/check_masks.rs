//! Coherent noncheck tactical construction. All occupants are opaque here;
//! these are legal-geometry rays, not transparent evaluation Influence rays.
use super::{DIRECTIONS, KNIGHT};
use crate::attacks::{influence_knight_targets, influence_rays};
use crate::movegen::MoveList;
use crate::position::Position;
use crate::types::{Color, Move, MoveKind, PieceKind, Square};

#[inline]
fn first(bits: u64, increasing: bool) -> u64 {
    if bits == 0 { 0 }
    else if increasing { bits & bits.wrapping_neg() }
    else { 1u64 << (63 - bits.leading_zeros()) }
}

// Empty prefix and nearest occupied endpoint, each still in this geometric ray.
#[inline]
fn prefix(ray: u64, occupied: u64, increasing: bool) -> (u64, u64) {
    let blocker = first(ray & occupied, increasing);
    let empty = if blocker == 0 { ray }
        else if increasing { ray & blocker.wrapping_sub(1) }
        else { ray & !blocker.wrapping_sub(1) & !blocker };
    (empty, blocker)
}

#[inline]
fn take_nearest(bits: &mut u64, increasing: bool) -> Square {
    debug_assert_ne!(*bits, 0);
    let index = if increasing { bits.trailing_zeros() }
        else { 63 - bits.leading_zeros() };
    *bits &= !(1u64 << index);
    Square(index as u8)
}

// Invocation-local base visibility. A source can be first blocker of at most
// one king ray; only that ray needs extending when the source is vacated.
struct CheckMasks {
    occupied: u64,
    diagonal: u64,
    orthogonal: u64,
    first_blockers: u64,
    king: Square,
}
impl CheckMasks {
    fn new(position: &Position, king: Square, diagonal: bool, orthogonal: bool) -> Self {
        let planes = position.attack_planes();
        let occupied = planes[0] | planes[1] | planes[2];
        let (rays, increasing) = influence_rays(king);
        let mut result = Self { occupied, diagonal: 0, orthogonal: 0,
            first_blockers: 0, king };
        for direction in 0..8 {
            if !(if direction < 4 { diagonal } else { orthogonal }) { continue; }
            let (empty, blocker) = prefix(rays[direction], occupied, increasing[direction]);
            if direction < 4 { result.diagonal |= empty; }
            else { result.orthogonal |= empty; }
            result.first_blockers |= blocker;
        }
        result
    }
    fn quiet_targets(&self, source: Square, kind: PieceKind) -> u64 {
        let base = match kind { PieceKind::Bishop => self.diagonal,
            PieceKind::Rook => self.orthogonal,
            PieceKind::Queen => self.diagonal | self.orthogonal,
            _ => unreachable!("tactical check-mask slider") };
        let bit = 1u64 << source.0;
        if self.first_blockers & bit == 0 { return base; }
        let df = source.file() as i8 - self.king.file() as i8;
        let dr = source.rank() as i8 - self.king.rank() as i8;
        let direction = match (df.signum(), dr.signum()) {
            (1, 1) => 0, (-1, -1) => 1, (-1, 1) => 2, (1, -1) => 3,
            (0, 1) => 4, (0, -1) => 5, (1, 0) => 6, (-1, 0) => 7,
            _ => unreachable!("source is a king-ray blocker"),
        };
        // A Bishop on an orthogonal blocker (or Rook on a diagonal blocker)
        // must not acquire the other checking family merely by vacating it.
        if (kind == PieceKind::Bishop && direction >= 4)
            || (kind == PieceKind::Rook && direction < 4) { return base; }
        let (rays, increasing) = influence_rays(self.king);
        let ray = rays[direction];
        let (extended, _) = prefix(ray, self.occupied & !bit, increasing[direction]);
        (base & !ray) | extended
    }
}

fn sliders<const KIND: usize>(position: &Position, out: &mut MoveList,
    side: Color, checks: &CheckMasks) {
    let kind = PieceKind::ALL[KIND];
    let directions = match kind { PieceKind::Bishop => 0..4,
        PieceKind::Rook => 4..8, PieceKind::Queen => 0..8,
        _ => unreachable!("tactical slider kind") };
    for &source in position.piece_squares(side, kind) {
        // Queen unions BOTH checking families independently of movement ray.
        let checking = checks.quiet_targets(source, kind);
        let (rays, increasing) = influence_rays(source);
        for direction in directions.clone() {
            let (empty, blocker) = prefix(rays[direction], checks.occupied, increasing[direction]);
            let mut quiets = empty & checking;
            while quiets != 0 {
                let target = take_nearest(&mut quiets, increasing[direction]);
                out.push(Move::new(source, target, MoveKind::Ordinary));
            }
            if blocker != 0 {
                let target = Square(blocker.trailing_zeros() as u8);
                let victim = position.board[target.0 as usize];
                if victim.color() != side && victim.kind() != PieceKind::King {
                    out.push(Move::new(source, target, MoveKind::Ordinary));
                }
            }
        }
    }
}

pub(super) fn generate_nonpawns(position: &Position, out: &mut MoveList,
    side: Color, enemy_king: Square) {
    let knights = position.piece_squares(side, PieceKind::Knight);
    if !knights.is_empty() {
        let checking = influence_knight_targets(enemy_king);
        for &source in knights {
            for (df, dr) in KNIGHT {
                let Some(target) = source.offset(df, dr) else { continue; };
                let victim = position.board[target.0 as usize];
                if !victim.is_empty() {
                    if victim.color() != side && victim.kind() != PieceKind::King {
                        out.push(Move::new(source, target, MoveKind::Ordinary));
                    }
                } else if checking & (1u64 << target.0) != 0 {
                    out.push(Move::new(source, target, MoveKind::Ordinary));
                }
            }
        }
    }
    let counts = position.counts[side.index()];
    let diagonal = counts[PieceKind::Bishop.index()] != 0 || counts[PieceKind::Queen.index()] != 0;
    let orthogonal = counts[PieceKind::Rook.index()] != 0 || counts[PieceKind::Queen.index()] != 0;
    if diagonal || orthogonal {
        let checks = CheckMasks::new(position, enemy_king, diagonal, orthogonal);
        sliders::<2>(position, out, side, &checks);
        sliders::<3>(position, out, side, &checks);
        sliders::<4>(position, out, side, &checks);
    }
    // King emits captures only, in the unchanged eight direction order.
    for &source in position.piece_squares(side, PieceKind::King) {
        for (df, dr) in DIRECTIONS {
            let Some(target) = source.offset(df, dr) else { continue; };
            let victim = position.board[target.0 as usize];
            if !victim.is_empty() && victim.color() != side && victim.kind() != PieceKind::King {
                out.push(Move::new(source, target, MoveKind::Ordinary));
            }
        }
    }
}
