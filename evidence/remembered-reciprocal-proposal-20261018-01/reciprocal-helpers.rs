// Construction-time metadata; both constructors already exclude zero groups.
fn group_reciprocal(count: usize) -> u64 {
    (1u64 << 32) / count as u64
}

#[inline]
fn group_remainder(key: u32, count: usize, reciprocal: u64) -> usize {
    // Preserve the original division-free path, including every count > u32::MAX.
    if (key as usize) < count {
        return key as usize;
    }
    // Here count <= key <= u32::MAX. The lower reciprocal quotient is at most
    // one below the exact quotient; all products fit u64 and q * count <= key.
    let quotient = (u64::from(key) * reciprocal) >> 32;
    let remainder = u64::from(key) - quotient * count as u64;
    if remainder >= count as u64 {
        (remainder - count as u64) as usize
    } else {
        remainder as usize
    }
}

