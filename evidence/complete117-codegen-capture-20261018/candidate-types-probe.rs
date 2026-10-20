// Candidate-only public auxiliary layouts; no old API counterpart claimed.
// INERT SOURCE TEMPLATE. No search entry is called or retained by this main.
use std::mem::{size_of,align_of};
fn item<T>(name:&str){println!("{} {} {}",name,size_of::<T>(),align_of::<T>());}
fn main(){
 item::<rook2::timing::TerminalPrefix>("TerminalPrefix");
 item::<rook2::timed_sequence::SuppliedOutcome>("SuppliedOutcome");
}
