The generic full-generator and default-call-site review shows no changed normalized instruction stream or frame in the scoped control functions. Control is the frozen correctedQ85 artifactd38ff03745c7fba981c22f12fdd7b10b78f539f9541faeb24b92bd263b116d45; candidate is61fdefb32daa9db4688f3c164ab7c94e057eef47f4459b87ad9c9a6ac5a263c1. Native source maps match the prepared baseline/variant, and generic flags/effective environments match. Mutable root does not define this comparison.

| Scoped function | Control bytes | Candidate bytes | Primary rsp subtraction (control/candidate) | Relocation-normalized instruction identity |
|---|---:|---:|---|---|
|full generate_legal|5445|5445|0x128 /0x128|same|
|default Q visit|7451|7451|0x4a8 /0x4a8|same|
|default full evaluation|2415|2415|0x138 /0x138|same|
|session adjudication|589|589|0x4a8 /0x4a8|same|
|capped replies|5423|3311|0x128 /0xf8|changed|

The capped function is2112 bytes smaller because LLVM now outlines a2300-byte movegen::pieces helper, which uses0xb8 stack bytes of its own and is called from several capped sites. The capped-plus-new-helper sum grows188 bytes before alignment. The checked early-king pass and remaining checked/unchecked piece passes can all use that helper. Thus neither the smaller capped symbol nor its48-byte smaller primary allocation proves a whole-kernel code/peak-stack/runtime improvement. Unchecked capped semantics are unchanged but its emitted shape also uses the outlined helper. Frequency, branch behavior, call overhead and avoided checked candidate work remain measurement questions.

Normalization removes file/disassembly addresses/comments, RIP displacements and absolute intra-function branch addresses while retaining mnemonic/register/immediate/stack operands and relative branch labels. It does not establish identity of every referenced data object or whole-program bytes. Exact original assemblies, normalized streams and diffs are retained alongside review_codegen.py/codegen-review.json. outlined-pieces-review.json records the added helper and named static call sites; these sites are not dynamic invocation counts. No codegen field is used as a mutable strict-check gate. No CPU/PGO/Callgrind measurement was run.
