// INERT SOURCE TEMPLATE. Compile/run only after exact117 functional pass and explicit parent clearance.
// main prints layouts only; the linked root entry is retained as a pointer and NEVER invoked.
use std::mem::{size_of,align_of};
fn item<T>(n:&str){println!("{} {} {}",n,size_of::<T>(),align_of::<T>());}
#[no_mangle]
#[inline(never)]
pub fn default_root(search:&mut rook2::engine::Search<false>,position:rook2::position::Position,
 history:&mut rook2::history::SearchHistory,controls:rook2::timed::Controls,limits:rook2::quiescence::Limits)
 ->Result<rook2::timed::Outcome,rook2::ordinary::Error>{search.run_work_timed(position,history,controls,limits)}
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

 item::<rook2::session::Session<false>>("SessionFalse");
 item::<rook2::session::Session<true>>("SessionTrue");
 item::<rook2::timed::Capture>("Capture");
 item::<rook2::post_lifecycle::CaptureSlot<rook2::timed::Capture>>("CaptureSlot");
 item::<Option<rook2::timed::Iteration>>("OptionalIteration");
 item::<Result<bool,rook2::quiescence::Stopped>>("ChargeReturned");
 item::<rook2::timing::Terminal>("Terminal");
 item::<rook2::work_clock::Ledger>("Ledger");
 std::hint::black_box(default_root as usize);
}
