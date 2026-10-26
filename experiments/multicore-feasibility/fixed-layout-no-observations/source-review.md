# Fixed original layout without observations

The new workspace is an exact copy of lean65 before this edit. Only src/colors_worker.rs changes; the other64 source inputs and the lean caller/receipt changes are preserved.

Packet, SideOutput, InventoryOutput, Metadata, Control, InventoryProduction and Shared field bodies are copied exactly from authoritative inventory65. Metric, Readiness and InventoryStats concrete storage is also restored, including Metric.sum_ns:u128 and all histogram arrays. Cells and Reader field bodies already match the original. No padding, repr adjustment, generic framework or layout sweep is added.

Every restored field has a valid value. Defaults and startup constructors initialize all metric/count/atomic storage to zero. Packet and Metadata constructors store None in unused timing/owner fields, and color output construction supplies zero timing scalars. These representation-required stores and initialization costs are admitted. No clock reads, observation record functions, histogram updates, production accounting RMWs or late accounting locks are restored. The installed receipt remains zero-sized and lifetime-free; disabled reporting remains exactly {"enabled":false}.

Numerical kernels, generation/domain admission, request/done/Flight and SC-latch rules,4096 spins, used-slice installation and scope boundaries remain the lean path. Input/output references still end before done and later request publication. Restored storage owns no new lease or admission decision.

The existing bounded40 controls are unchanged: colors_worker::lifecycle_tests29, evaluator::inventory_four_tests8 and evaluator::colors_lifecycle_tests3. The worker test suffix is byte-identical to lean65; no observation logic is enabled under cfg(test). Prior numerical/cache and generation evidence remains historical reuse; no new matrix is proposed.

Source equality is not compiled-layout admission. Before data, the parent must match allocation size/alignment and concrete hot offsets/sizes against original36c40 using the existing image review table. A mismatch must be resolved or returned as failed admission, without arbitrary padding. Matching representation does not establish runtime Bmod64, cache misses or isolated synchronization cost. No build, test, native execution or Git operation was performed for this source task.
