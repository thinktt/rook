use std::mem::{size_of,align_of};
fn item<T>(n:&str){println!("{} {} {}",n,size_of::<T>(),align_of::<T>());}
#[no_mangle]
#[inline(never)]
pub fn guarded_root(search:&mut rook2::engine::Search<false>,position:rook2::position::Position,
 history:&mut rook2::history::SearchHistory,controls:rook2::timed::Controls,limits:rook2::quiescence::Limits)
 ->Result<rook2::timed::Outcome,rook2::ordinary::Error>{search.run_work_timed_without_iio(position,history,controls,limits)}
fn main(){
 item::<rook2::engine::Search<false>>("SearchFalse");item::<rook2::engine::Search<true>>("SearchTrue");
 item::<rook2::quiescence::Stats>("Stats");item::<rook2::evaluator::Node>("Node");item::<rook2::evaluator::Retained>("Retained");
 item::<rook2::evaluator::Evaluation>("Evaluation");item::<rook2::evaluator::Evaluator<false>>("EvaluatorFalse");
 item::<rook2::position::Position>("Position");item::<rook2::ordinary::Outcome>("OrdinaryOutcome");
 item::<rook2::first_iteration::Outcome>("FirstOutcome");item::<rook2::quiescence::Outcome>("QOutcome");
 item::<rook2::timed::Outcome>("TimedOutcome");item::<rook2::timed::Controls>("Controls");

 item::<rook2::quiescence::Stopped>("Stopped");
 item::<Result<i32,rook2::quiescence::Stopped>>("OrdinaryReturned");
 item::<rook2::ordinary::Error>("OrdinaryError");
 item::<Result<rook2::timed::Outcome,rook2::ordinary::Error>>("TimedReturned");
 std::hint::black_box(guarded_root as usize);
}
