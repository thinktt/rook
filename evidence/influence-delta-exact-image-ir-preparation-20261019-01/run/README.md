# Exact generic25/30 case08 instruction discriminator

Two fresh original case08 replays, one per unchanged exact generic executable, pass the original assertion live and independently offline. Actual profile driverc5b001/session63430 completed40bd12/0; verifier428e75/0; parent incoming-arc reconciliationba000d/0. Frozen25generic2940ae5c… and30genericB9cc941d… remain byte-stable with the same recorded compiler/flags. Valgrind3.24.0 client execution was observed on guestCPU14; helpers/annotations stayed on housekeeping. All input pins remain stable.

| Disjoint measured scope |25 simulated Ir|30 simulated Ir|
|---|---:|---:|
|Whole native lifetime|4656895448|4676072765|
|Ordinary map construction descendants|94288813|99328933|
|Ordinary function self, all file partitions|289974619|304095743|
|Q function self|73575647|73575647|
|Q fresh-map descendants|64387905|64387905|
|Root fresh-map descendant|558|558|
|Evaluation-consumer self family|1294760410|1294760410|
|Root/host self family|108507|108507|
|All remaining self|2839798989|2839815062|

The last eight rows partition the whole lifetime exactly once. Update-inclusive already contains signed rays; their21447647Ir are not added again. Construction calls reconcile to the independent same-case census: control361836 fresh;30 has147171 fresh plus214665 updates. Ordinary first-fill count remains222480. Full raw IDs/suffixes, self rows, arcs and unassigned source/core scopes are retained in partition.json. All caller construction arcs are in parent-construction-arcs.json.

Whole-lifetime Ir rises19177317 (+0.411805%). Ordinary construction descendants rise5040120 (+5.345%), and ordinary self rises14121124. That self owner includes unrelated inline work and caller transport; the entire increase is not assigned to any particular copy/branch. Other self differs16073; no unsupported startup attribution is imposed. No outlined CurrentInfluence::fill calls execute in this case, so its known temporary copy is not an explanation of08. The updater's actual inclusive95909876Ir consists of74462229self+21447647signed rays.

This is a concrete machine-work penalty for the exact08 lifetime despite high reuse eligibility. The earlier9548→2327 profile writes came from122 separate legal samples, not an observed whole08 write count. Source-operation counts and mixed-context averages do not establish paired eligible-node kernel costs or universal speed ratios. Under this measured workload, replacement does not reduce the selected construction work; the larger35 construction pool still needs its own discriminator before selecting a hybrid or abandoning the direction.

These are simulated client instructions with cache/branch simulation disabled, not hardware retired instructions, cycles/CPI, native CPU speed or final qualification. The native08 CPU pilot and this profile are separate runs. Both failed production trials remain parked; no new performance candidate or source promotion follows this diagnostic. Candidate25 stays retained.
