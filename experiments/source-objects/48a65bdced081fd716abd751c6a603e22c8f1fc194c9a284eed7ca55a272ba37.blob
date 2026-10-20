// Bounded public-field offset readout only; no instance or search is constructed.
use std::mem::offset_of;
fn main() {
 println!("SearchFalse.evaluator {}", offset_of!(rook2::engine::Search<false>, evaluator));
 println!("SearchFalse.config {}", offset_of!(rook2::engine::Search<false>, config));
 println!("Stats.nodes {}", offset_of!(rook2::quiescence::Stats, nodes));
 println!("Stats.iio_initial_phases {}", offset_of!(rook2::quiescence::Stats, iio_initial_phases));
 println!("Stats.accumulated_extension_uses {}", offset_of!(rook2::quiescence::Stats, accumulated_extension_uses));
 println!("OrdinaryOutcome.stats {}", offset_of!(rook2::ordinary::Outcome, stats));
 println!("FirstOutcome.stats {}", offset_of!(rook2::first_iteration::Outcome, stats));
 println!("QOutcome.stats {}", offset_of!(rook2::quiescence::Outcome, stats));
}
