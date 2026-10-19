# Experiment30 in-place producer backend gate

Mechanism survives this bounded static gate. The actual default image updates the owned CurrentInfluence payload on both demand paths, rather than invoking a by-value derived-map producer. This is a backend finding only; native182 and timing remain parent-owned, and no speed or adoption conclusion follows.

Image b9cc941d7dbc1ef458f908a20ac82ef8e18b70625d14fd3dee7b4ce380e0d6f8 (7,024,760 bytes) is compared against frozen29 generic2b0e8ebb. Receipt comparison records exactly influence.rs/ordinary.rs changed, with other source entries unchanged; compared compiler/flag/tool fields are recorded separately. All static commands ran on CPUs0-5,8-13 with HOME TMPDIR. No builds, probes, engines, tests, profiles, archives, Git or source edits occurred.

The emitted update_ordinary at0x211d0 is2874B, explicit rsp reservation152B plus six saved registers. Old derive was3088B/rsp280. It saves the incoming map pointer at rsp+8 and uses that pointer for actual scalar writes and signed-ray calls (for example0x21231–0x21247); normal return0x21c3c–0x21c4d contains no128B map return. There is no local128B map load/store series in this updater. The only SIMD stack writes in its captured body are16B panic-construction stores. The by-value derive wrapper is cfg(test)-only in source; symbol absence alone is not the proof—the actual producer body and callers are captured.

Direct demand: ordinary0x3e60f establishes payload rsp+0x391 beside its marker rsp+0x390. At0x3e69e–0x3e6dc it copies the parent128B directly into that payload, then passes precisely that pointer as rdi at0x3e6e8 to the0x3e6f5 update call. Relocation e2ea0 resolves to211d0. Thus the required parent copy remains, but updater-local map staging and map return are removed on this path.

Outlined demand: ordinary0x3fefb calls fill with self=rsp+0x388. Fill0x3d478 computes self+9 (the same payload), copies the initialized parent map there, sets rdi to self+9 at0x3d4c9, restores its frame and tail-jumps via e2ea0 to update_ordinary at0x3d4d4. The old fill→by-value derive→returned map chain is removed. However, the compiler still stages parent128B through fill's rsp temporary (0x3d42e–0x3d470 then0x3d47c–0x3d4bf). Do not describe this path as a single-copy implementation.

Residual fallback/ready costs: fill is320B versus29's158B and still reserves128B plus saved rbx. Unlike29, this prologue now precedes the ready marker check; even ready fill enters that frame. On the delta path fill restores its frame before tail-jumping, so fill128 and update152 are not simultaneously live on that edge. Fresh fallback still calls build into fill's128B temporary then copies it to payload. The direct ordinary fresh fallback at0x3e73a similarly builds into rsp+0x120 and copies to payload. These residuals can affect net cost; static inspection does not predict their dynamic frequency or traffic cost.

| Body |29 bytes|30 bytes|29/30 explicit rsp reservation|
|---|---:|---:|---:|
|ordinary|9019|9054|1064/1064|
|fill|158|320|128/128|
|fresh Influence::build|4787|4787|264/264|
|Q visit|7224|7224|1224/1224|

Ordinary, fresh and Q also save six registers; fill saves one. Fresh/Q quick scope shows unchanged extent/frame, not an exhaustive machine/data equivalence proof. The optional address-normalized shape comparison is false for both in quick-shape.json; no equivalence claim is based on it and no further attribution was required for this narrow producer gate. Existing signed-ray calls remain; no whole-program/ABI/sizeof proof or dynamic spill/cache claim is made.

Evidence: update.asm, fill.asm, ordinary.asm, ordinary-demand-windows.txt, selected-relocations.txt and functions.json contain exact operands, addresses and bounded raw disassemblies. Parent retains the decision to run182 and the frozen pilot. All static children have returned exit0; no further scans are scheduled.
