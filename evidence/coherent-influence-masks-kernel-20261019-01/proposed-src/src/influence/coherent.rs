//! Private coherent-placement producer: scalar leapers, masked SIMD sliders.
//! No cache, parent map, persistent state, relation queries or changed byte format.
use super::{Contribution, Influence};
use crate::attacks::influence_rays;
use crate::geometry::{DIRECTIONS, KING_TARGETS, KNIGHT_SOURCES, PAWN_TARGETS};
use crate::position::Position;
use crate::types::{Color, PieceKind, Square};
use std::arch::x86_64::{__m128i, _mm_add_epi8, _mm_loadu_si128, _mm_or_si128,
    _mm_set_epi64x, _mm_slli_epi16, _mm_storeu_si128};

// Exactly 256 * 8 = 2048 immutable bytes. Little-endian byte lane i represents
// bit i. The only consumers use x86-64 baseline SSE2; no feature dispatch.
const fn expansion_table() -> [u64; 256] {
    let mut result = [0u64; 256];
    let mut pattern = 0;
    while pattern < 256 {
        let mut lane = 0;
        while lane < 8 {
            result[pattern] |= (((pattern >> lane) & 1) as u64) << (8 * lane);
            lane += 1;
        }
        pattern += 1;
    }
    result
}
static EXPANSION: [u64; 256] = expansion_table();

pub(super) fn build(position: &Position) -> Influence {
    let mut result = Influence { profiles: [[0; 64]; 2] };
    let planes = position.attack_planes();
    for side in [Color::White, Color::Black] {
        // Retain actual scalar P/N/K source lists, targets, order and wrapping.
        for &source in position.piece_squares(side, PieceKind::Pawn) {
            debug_assert!(source.0 < 64);
            let targets = &PAWN_TARGETS[side.index()][(source.0 & 63) as usize];
            for &target in &targets.squares[..targets.len as usize] {
                result.add(side, Square(target & 63), Contribution::Pawn as u8);
            }
        }
        for &source in position.piece_squares(side, PieceKind::Knight) {
            debug_assert!(source.0 < 64);
            let targets = &KNIGHT_SOURCES[(source.0 & 63) as usize];
            for &target in &targets.squares[..targets.len as usize] {
                result.add(side, Square(target & 63), Contribution::Minor as u8);
            }
        }
        for &source in position.piece_squares(side, PieceKind::King) {
            debug_assert!(source.0 < 64);
            let targets = &KING_TARGETS[(source.0 & 63) as usize];
            for &target in &targets.squares[..targets.len as usize] {
                result.add(side, Square(target & 63), Contribution::Weak as u8);
            }
        }
        let bishops = position.piece_squares(side, PieceKind::Bishop);
        let rooks = position.piece_squares(side, PieceKind::Rook);
        let queens = position.piece_squares(side, PieceKind::Queen);
        if bishops.is_empty() && rooks.is_empty() && queens.is_empty() {
            continue; // No slider means no vector load/store/setup for this side.
        }
        let mut sums = ColorSums::load(&result.profiles[side.index()]);
        for &source in bishops {
            let (normal, weak) = slider_masks::<2>(planes, side, source);
            sums.add::<4>(normal, weak); // Minor16.
        }
        for &source in rooks {
            let (normal, weak) = slider_masks::<3>(planes, side, source);
            sums.add::<2>(normal, weak); // Rook4.
        }
        for &source in queens {
            let (normal, weak) = slider_masks::<4>(planes, side, source);
            sums.add::<1>(normal, weak); // Queen2.
        }
        sums.store(&mut result.profiles[side.index()]);
    }
    result
}

#[inline]
fn first(blockers: u64, increasing: bool) -> u64 {
    if blockers == 0 { 0 }
    else if increasing { blockers & blockers.wrapping_neg() }
    else { 1u64 << (63 - blockers.leading_zeros()) }
}
#[inline]
fn through(ray: u64, blocker: u64, increasing: bool) -> u64 {
    if blocker == 0 { ray }
    else if increasing { ray & (blocker | blocker.wrapping_sub(1)) }
    else { ray & !blocker.wrapping_sub(1) }
}

/// For one source, original and weakened targets are disjoint. Different
/// sources must still be emitted separately to retain contribution multiplicity.
#[inline]
pub(super) fn slider_masks<const KIND: usize>(planes: &[u64; 4], side: Color,
    source: Square) -> (u64, u64) {
    let own = if side == Color::Black { planes[3] } else { !planes[3] };
    let occupied = planes[0] | planes[1] | planes[2];
    let queens = planes[0] & !planes[1] & planes[2] & own;
    let pawns = planes[0] & !planes[1] & !planes[2] & own;
    let rooks = !planes[0] & !planes[1] & planes[2] & own;
    let bishops = planes[0] & planes[1] & !planes[2] & own;
    let enemy_kings = !planes[0] & planes[1] & planes[2] & !own;
    let (rays, increasing) = influence_rays(source);
    let directions = match KIND { 2 => 0..4, 3 => 4..8, 4 => 0..8,
        _ => unreachable!("not an influence slider") };
    let mut normal = 0;
    let mut weak = 0;
    for direction in directions {
        let diagonal = direction < 4;
        let transparent = queens | enemy_kings | if diagonal { bishops } else { rooks };
        let ray = rays[direction];
        let stop = first(ray & occupied & !transparent, increasing[direction]);
        let mut visited = through(ray, stop, increasing[direction]);
        let step = DIRECTIONS[direction];
        let forward = if side == Color::White { 1 } else { -1 };
        if diagonal && step.1 == forward && stop & pawns != 0 {
            // Add exactly one square past the stopping pawn, without inspecting
            // that square's occupant. Intersect R to guard its board edge.
            let delta = step.0 as i16 + 8 * step.1 as i16;
            let extra = if delta > 0 { stop << delta as u32 }
                else { stop >> (-delta) as u32 };
            visited |= extra & ray;
        }
        let queen = first(visited & queens, increasing[direction]);
        let original = through(visited, queen, increasing[direction]);
        normal |= original;
        weak |= visited & !original;
    }
    (normal, weak)
}

struct ColorSums { chunks: [__m128i; 4] }
impl ColorSums {
    #[inline]
    fn load(bytes: &[u8; 64]) -> Self {
        // SAFETY: x86-64 supplies SSE2. Four unaligned16B reads cover exactly
        // this64B array; no reference alignment or initialization is assumed.
        unsafe { Self { chunks: [
            _mm_loadu_si128(bytes.as_ptr().cast()),
            _mm_loadu_si128(bytes.as_ptr().add(16).cast()),
            _mm_loadu_si128(bytes.as_ptr().add(32).cast()),
            _mm_loadu_si128(bytes.as_ptr().add(48).cast()),
        ] } }
    }
    #[inline]
    fn store(&self, bytes: &mut [u8; 64]) {
        // SAFETY: the same four disjoint16B ranges are writable within bytes.
        unsafe { for i in 0..4 {
            _mm_storeu_si128(bytes.as_mut_ptr().add(16 * i).cast(), self.chunks[i]);
        } }
    }
    #[inline]
    fn add<const SHIFT: i32>(&mut self, normal: u64, weak: u64) {
        debug_assert_eq!(normal & weak, 0);
        debug_assert!((0..=6).contains(&SHIFT));
        // SAFETY: baseline SSE2; table indices are masked to bytes. Expanded
        // byte values0/1 shifted at most6 cannot carry into adjacent bytes,
        // even though slli operates on16-bit lanes. paddb wraps each byte.
        unsafe {
            if weak == 0 {
                for i in 0..4 {
                    let add = _mm_slli_epi16::<SHIFT>(expand((normal >> (16 * i)) as u16));
                    self.chunks[i] = _mm_add_epi8(self.chunks[i], add);
                }
            } else {
                for i in 0..4 {
                    let original = _mm_slli_epi16::<SHIFT>(expand((normal >> (16 * i)) as u16));
                    let add = _mm_or_si128(original, expand((weak >> (16 * i)) as u16));
                    self.chunks[i] = _mm_add_epi8(self.chunks[i], add);
                }
            }
        }
    }
}
#[inline]
unsafe fn expand(bits: u16) -> __m128i {
    // Both scalar table loads are in bounds; low8 squares precede high8.
    _mm_set_epi64x(EXPANSION[(bits >> 8) as usize] as i64,
        EXPANSION[(bits & 255) as usize] as i64)
}

#[cfg(test)]
pub(super) fn emit_for_test<const SHIFT: i32>(previous: [u8; 64], normal: u64,
    weak: u64) -> [u8; 64] {
    let mut bytes = previous;
    let mut sums = ColorSums::load(&bytes);
    sums.add::<SHIFT>(normal, weak);
    sums.store(&mut bytes);
    bytes
}
