//! Rook2: an independent implementation of the KingRE behavioral specification.
//!
//! Shared native search, evaluation and persistent session state. Public wire
//! servicing and diagnostic translation remain cold boundaries; complete
//! behavioral and performance qualification is still pending.

pub mod activity;
mod attacks;
pub mod clock;
pub mod development;
pub mod endgame;
pub mod engine;
mod eval_basis;
pub mod evaluation;
pub mod evaluator;
pub mod first_iteration;
mod geometry;
pub mod history;
pub mod host;
pub mod identity;
pub mod influence;
pub mod movegen;
pub mod ordinary;
pub mod ordinary_policy;
pub mod output;
pub mod parameters;
pub mod pawn_progress;
pub mod pawn_structure;
pub mod pawn_terms;
pub mod position;
pub mod post_lifecycle;
pub mod positional_terms;
pub mod quiescence;
pub mod quiescence_policy;
mod relation_table;
pub mod remembered;
pub mod root_schedule;
pub mod session;
pub mod shelter;
pub mod tactical;
mod time_powers;
pub mod timed;
pub mod timed_sequence;
pub mod timing;
pub mod types;
pub mod wire;
pub mod work_clock;
