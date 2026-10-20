// Force only the old const-false fixed entry's specialization into an object.
// This is a codegen probe; it has no main and is never executed.
#[no_mangle]
pub fn default_fixed_entry(search: &mut rook2::engine::Search<false>,
 position: rook2::position::Position, history: &mut rook2::history::SearchHistory,
 completed: u8, limits: rook2::quiescence::Limits)
 -> Result<rook2::ordinary::Outcome, rook2::ordinary::Error>
{ search.run_iterations(position, history, completed, limits) }
