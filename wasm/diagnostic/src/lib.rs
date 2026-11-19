//! The existing diagnostic parser/dispatcher, with a string transport for WASM.
#[path = "../../abi.rs"]
mod abi;
#[path = "../../../diagnostic/src/main.rs"]
#[allow(dead_code)]
mod adapter;

#[no_mangle]
pub unsafe extern "C" fn rook_diagnostic(pointer: *const u8, length: usize) -> u32 {
    let result = serde_json::from_str(abi::text(pointer, length))
        .map_err(|e| e.to_string()).and_then(|request| adapter::response(&request));
    match result {
        Ok(value) => { abi::emit(1, &format!("{value}\n")); 0 }
        Err(error) => { abi::emit(2, &format!("rook2-diag: {error}\n")); 1 }
    }
}
