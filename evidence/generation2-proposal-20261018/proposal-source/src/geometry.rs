//! Immutable valid board steps shared by legality and evaluation.
use crate::types::Square;

pub(crate) const KNIGHT: [(i8, i8); 8] = [
    (1, 2),
    (-1, -2),
    (-1, 2),
    (1, -2),
    (2, 1),
    (-2, -1),
    (-2, 1),
    (2, -1),
];
pub(crate) const DIRECTIONS: [(i8, i8); 8] = [
    (1, 1),
    (-1, -1),
    (-1, 1),
    (1, -1),
    (0, 1),
    (0, -1),
    (1, 0),
    (-1, 0),
];

#[derive(Clone, Copy)]
#[repr(C)]
pub(crate) struct Ray {
    pub(crate) squares: [u8; 7],
    pub(crate) len: u8,
}

#[repr(align(64))]
pub(crate) struct RayTable(pub(crate) [[Ray; 8]; 64]);

const fn attack_rays() -> RayTable {
    let empty = Ray {
        squares: [0; 7],
        len: 0,
    };
    let mut table = [[empty; 8]; 64];
    let mut square = 0;
    while square < 64 {
        let mut direction = 0;
        while direction < 8 {
            let (df, dr) = DIRECTIONS[direction];
            let mut cursor = Square(square as u8);
            while let Some(next) = cursor.offset(df, dr) {
                let ray = &mut table[square][direction];
                ray.squares[ray.len as usize] = next.0;
                ray.len += 1;
                cursor = next;
            }
            direction += 1;
        }
        square += 1;
    }
    RayTable(table)
}

#[derive(Clone, Copy)]
pub(crate) struct Leaps {
    pub(crate) squares: [u8; 8],
    pub(crate) len: u8,
}

const fn knight_sources() -> [Leaps; 64] {
    let mut table = [Leaps {
        squares: [0; 8],
        len: 0,
    }; 64];
    let mut square = 0;
    while square < 64 {
        let mut direction = 0;
        while direction < 8 {
            let (df, dr) = KNIGHT[direction];
            if let Some(from) = Square(square as u8).offset(df, dr) {
                let leaps = &mut table[square];
                leaps.squares[leaps.len as usize] = from.0;
                leaps.len += 1;
            }
            direction += 1;
        }
        square += 1;
    }
    table
}

pub(crate) static ATTACK_RAYS: RayTable = attack_rays();
pub(crate) static KNIGHT_SOURCES: [Leaps; 64] = knight_sources();
const fn king_targets() -> [Leaps; 64] {
    let mut table = [Leaps {
        squares: [0; 8],
        len: 0,
    }; 64];
    let mut square = 0;
    while square < 64 {
        let mut direction = 0;
        while direction < 8 {
            let (df, dr) = DIRECTIONS[direction];
            if let Some(target) = Square(square as u8).offset(df, dr) {
                let entry = &mut table[square];
                entry.squares[entry.len as usize] = target.0;
                entry.len += 1;
            }
            direction += 1;
        }
        square += 1;
    }
    table
}

#[derive(Clone, Copy)]
pub(crate) struct PawnTargets {
    pub(crate) squares: [u8; 2],
    pub(crate) len: u8,
}
const fn pawn_targets() -> [[PawnTargets; 64]; 2] {
    let mut table = [[PawnTargets {
        squares: [0; 2],
        len: 0,
    }; 64]; 2];
    let mut side = 0;
    while side < 2 {
        let forward = if side == 0 { 1 } else { -1 };
        let mut square = 0;
        while square < 64 {
            let mut direction = 0;
            while direction < 2 {
                let df = if direction == 0 { -1 } else { 1 };
                if let Some(target) = Square(square as u8).offset(df, forward) {
                    let entry = &mut table[side][square];
                    entry.squares[entry.len as usize] = target.0;
                    entry.len += 1;
                }
                direction += 1;
            }
            square += 1;
        }
        side += 1;
    }
    table
}
pub(crate) static KING_TARGETS: [Leaps; 64] = king_targets();
pub(crate) static PAWN_TARGETS: [[PawnTargets; 64]; 2] = pawn_targets();
