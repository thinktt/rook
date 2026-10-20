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
 item::<rook2::root_schedule::Row>("Row");item::<rook2::root_schedule::Iteration>("RootIteration");
 item::<rook2::root_schedule::Attempt>("Attempt");item::<rook2::root_schedule::Completed>("Completed");
 item::<rook2::root_schedule::Returned>("Returned");
 println!("RowOffsets {} {} {}",std::mem::offset_of!(rook2::root_schedule::Row,id),std::mem::offset_of!(rook2::root_schedule::Row,score),std::mem::offset_of!(rook2::root_schedule::Row,work));
 std::hint::black_box(default_root as usize);
}
