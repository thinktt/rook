# Correct the unsupported indirect-call label

The frozen runtime-tier review described its two unresolved `call r15` instructions as “host/callback transfers.” That attribution was unsupported and is withdrawn. Its saved additional-facts table correctly retained only `call r15`, without a resolved target. Equal call-target counts were not proof of those two targets.

The subsequent child-application source review identifies register-mediated memcpy transport in the saved current62 complete ordinary body. This is separate later evidence and will retain its own exact source/relocation/operand chain. Do not infer dynamic frequency or CPU cost from the six direct memcpy entries alone; register-mediated calls need independent resolution.

The original review, timing-admission hashes, pilot immutable inputs, raw captures and first archive are preserved byte-for-byte. This correction changes no #65 source, timing sample, fixed decision threshold or park outcome. It does not authorize a new source prototype or measurement.
