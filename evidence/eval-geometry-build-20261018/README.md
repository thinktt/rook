# Initial compile-only failure

The first table-sharing edit removed three constants still used by the existing
king-pressure function. Compilation failed with E0425; no engine or test binary
ran. The build/native logs and verified failed source archive are retained.
The corrected independent experiment is in the sibling `-02` build/check
folders. This failure contributes no timing or conformance result.
