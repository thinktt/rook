//! Configuration-time permission snapshot, not a physical-core/capacity estimate.

#[cfg(target_os = "linux")]
pub(crate) fn permitted_cpus() -> Result<usize, String> {
    extern "C" {
        fn sched_getaffinity(pid: i32, bytes: usize, mask: *mut usize) -> i32;
    }
    // Start with the usual 1024-bit mask. Linux may require a larger buffer
    // for its configured CPU namespace even when few CPUs are currently allowed.
    let mut mask = vec![0usize; 1024 / usize::BITS as usize];
    loop {
        let bytes = mask.len() * std::mem::size_of::<usize>();
        // pid0 selects the configuring thread. The aligned writable mask spans
        // exactly `bytes`; no affinity is changed, and no pointer is retained.
        if unsafe { sched_getaffinity(0, bytes, mask.as_mut_ptr()) } == 0 {
            let count = mask.iter().map(|word| word.count_ones() as usize).sum();
            return if count == 0 {
                Err("permitted CPU affinity is empty".into())
            } else { Ok(count) };
        }
        let error = std::io::Error::last_os_error();
        // Keep a bounded query buffer; an unsupported mask is an explicit
        // configuration error rather than an invented CPU-count fallback.
        if error.kind() != std::io::ErrorKind::InvalidInput || bytes >= 65536 {
            return Err(format!("cannot query permitted CPU affinity: {error}"));
        }
        mask.resize(mask.len() * 2, 0);
    }
}

#[cfg(not(target_os = "linux"))]
pub(crate) fn permitted_cpus() -> Result<usize, String> {
    Err("multi-thread affinity policy is currently supported only on Linux".into())
}
