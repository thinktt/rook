//! Rook2: an independent implementation of the KingRE behavioral specification.
//!
//! This initial crate is an implementation scaffold. It currently makes no
//! behavioral conformance or engine-performance claim. Native computation will
//! live here; protocol and diagnostic translation remain at cold boundaries.

pub mod activity;
pub mod remembered;
pub mod shelter;
pub mod pawn_structure;
pub mod development;
mod eval_basis;
pub mod evaluation;
pub mod identity;
pub mod influence;
pub mod movegen;
pub mod position;
pub mod types;
