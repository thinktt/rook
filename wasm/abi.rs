//! Minimal UTF-8 host boundary. The JS host owns copies of emitted bytes.
#[link(wasm_import_module = "rook")]
extern "C" {
    fn output(channel: u32, pointer: *const u8, length: usize);
    fn poll_command(pointer: *mut u8, capacity: usize) -> i32;
    fn epoch_seconds() -> u32;
}

pub fn emit(channel: u32, text: &str) {
    unsafe { output(channel, text.as_ptr(), text.len()) }
}
pub fn seconds() -> u32 { unsafe { epoch_seconds() } }
pub fn poll() -> std::io::Result<Option<String>> {
    let mut bytes = [0u8; 1024];
    let length = unsafe { poll_command(bytes.as_mut_ptr(), bytes.len()) };
    if length == -1 { return Ok(None); }
    if length < 0 || length as usize > bytes.len() {
        return Err(std::io::Error::other("invalid search command record"));
    }
    String::from_utf8(bytes[..length as usize].to_vec()).map(Some)
        .map_err(std::io::Error::other)
}

// Only buffers returned here may be freed; length must be identical.
#[no_mangle]
pub extern "C" fn rook_alloc(length: usize) -> *mut u8 {
    Box::into_raw(vec![0u8; length].into_boxed_slice()) as *mut u8
}
#[no_mangle]
pub unsafe extern "C" fn rook_free(pointer: *mut u8, length: usize) {
    drop(Box::from_raw(std::ptr::slice_from_raw_parts_mut(pointer, length)));
}
pub unsafe fn text<'a>(pointer: *const u8, length: usize) -> &'a str {
    std::str::from_utf8(std::slice::from_raw_parts(pointer, length)).expect("UTF-8 input")
}

#[no_mangle]
pub extern "C" fn rook_init() {
    std::panic::set_hook(Box::new(|info| emit(2, &format!("rook-wasm panic: {info}\n"))));
}
