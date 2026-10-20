use std::mem::{size_of,align_of};
fn item<T>(n:&str){println!("{} {} {}",n,size_of::<T>(),align_of::<T>());}
#[no_mangle] #[inline(never)]
pub fn default_position(p:&mut rook2::position::Position,m:rook2::types::Move){p.apply_unchecked(m)}
#[no_mangle] #[inline(never)]
pub fn default_node(n:&rook2::evaluator::Node,r:&rook2::evaluation::RootContext,m:rook2::types::Move)->rook2::evaluator::Node{n.child(r,m)}
fn main(){
 item::<rook2::engine::Search<false>>("SearchFalse");item::<rook2::engine::Search<true>>("SearchTrue");
 item::<rook2::position::Position>("Position");
 item::<rook2::evaluator::Node>("Node");item::<rook2::evaluator::Retained>("Retained");
 item::<rook2::evaluator::Evaluation>("Evaluation");item::<rook2::evaluator::Evaluator<false>>("EvaluatorFalse");
 item::<rook2::ordinary::Outcome>("OrdinaryOutcome");item::<rook2::quiescence::Outcome>("QOutcome");item::<rook2::timed::Outcome>("TimedOutcome");
 println!("NodeOffsets {} {}",std::mem::offset_of!(rook2::evaluator::Node,retained),std::mem::offset_of!(rook2::evaluator::Node,position));
 std::hint::black_box(default_position as usize);std::hint::black_box(default_node as usize);
}
