# Recorded cold diagnostic build

The receipt and verified source archive bind the adapter's Cargo/src bytes.
The linked native library has a separate source closure: source maps in the
sibling diagnostic check folder match the verified native archive under
`../generation-integrated-build-20261018/`. Extract that as the parent crate
and this archive into its `diagnostic/` directory to reconstruct the path layout.
Pinned Cargo.lock registry versions/checksums are separate public dependencies.
This build is not the ordinary executable or a performance sample.
