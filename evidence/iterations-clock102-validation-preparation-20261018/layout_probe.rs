// Future diagnostic layout readout, compiled only after explicit execution clearance.
use std::mem::{size_of, align_of};
fn item<T>(name: &str) { println!("{} {} {}", name, size_of::<T>(), align_of::<T>()); }
fn main() {
    item::<rook2::quiescence::Stats>("Stats");
    item::<rook2::quiescence::Work>("Work");
    item::<rook2::engine::Search<false>>("SearchFalse");
    item::<rook2::engine::Search<true>>("SearchTrue");
    item::<rook2::ordinary::Outcome>("OrdinaryOutcome");
    item::<rook2::first_iteration::Outcome>("FirstOutcome");
    item::<rook2::quiescence::Outcome>("QOutcome");
    item::<rook2::evaluator::Node>("Node");
    item::<rook2::evaluator::Retained>("Retained");
    item::<rook2::evaluator::Evaluation>("Evaluation");
    item::<rook2::evaluator::Evaluator<false>>("EvaluatorFalse");
    item::<rook2::position::Position>("Position");
}
