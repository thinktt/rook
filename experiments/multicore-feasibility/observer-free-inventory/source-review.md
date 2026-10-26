# Observer-free inventory source review

Base: frozen inventory65 in /home/legolas/rook2-experiments/workspaces/epoch-inventory-four-20261026-01, copied unchanged before edits to observer-free-inventory-20261026-01. Only colors_worker.rs, evaluator.rs, ordinary.rs and evaluator/inventory_four_tests.rs change. No new Rust source file, numerical kernel, generator, admission, thread policy or whole-helper transport change.

Removed production clocks, histogram/count storage, InventoryProduction atomic accounting, owner_ready, and late demand/discard accounting calls. InventoryReceipt is now a private zero-sized installed marker with no destructor, epoch key or transport lease. Some is constructed only after used-slice/length installation; None retains original generation fallback. Ordinary consumes the marker at the original producer point; early returns drop it locally. Existing semantic N/R/generated charges, ordering and extension initialization stay at their original demand. Reports for every mode are exactly {"enabled":false}.

No removed count owns admission or lifetime. Metadata.colors_completed prevented duplicate observation counts only. Inventory participation, Published/Joined/Discarding, checked epochs, initialized cells, request/done and active-scope ownership remain. Joined still retains input through numerical FULL until the real third-reader acquisition. Output slice reads still end before Flight::None and the next private request release. The per-reader terminal/parking and reverse edges do not rely on observation locks. Fourteen protocol function bodies, including inventory_domain, own_request, terminal, both_done, inventory_done, signal_completion, waits, park, release_scope, publish_terminal and shutdown, compare byte-identical. retire_flight now only discards metadata after its unchanged caller's retirement check. The single-waiter SC exchanges and4096 spins are untouched.

The test-only ProtocolSnapshot reads existing generation/request/done/flight state; it writes no counters and re-enables no removed observations. Actual null controls retain semantic result/work/N/R/state comparisons, require real ordinary inventory publication, and show later FULL epochs beyond the parent epoch. Public/FRESH callbacks still assert parking; Q/root checks use the unchanged private inventory request. Native unsorted special/checked lists and the explicit test-only unavailable control remain.

Old50 controls partition as follows:

- 16 worker bodies and3 scope controls remain unchanged and are selected again.
- 13 worker controls and8 actual ordinary/evaluator controls are adapted to the lean path.
- 2 histogram-only controls are removed: colors_sparse_counts_partition_completed_discarded_and_failed_samples and colors_histogram_zero_and_positive_bucket_boundaries. Their historical evidence is not new coverage.
- 8 unchanged evaluator numerical/cache controls are retained as historical evidence, not selected in this affected40 run.

The former sampled installed-receipt control is now observer_free_receipt_and_report_need_no_accounting_lock: it executes real installation and later epochs, checks the marker has zero size/no destructor, and drops it plus requests disabled reporting while Control is already held. This checks the absence of the old late accounting lock, without timers or statistics. Input/output delays, close/failure, sparse participation, unavailable fallback and reverse-edge controls exercise the same production path.

The retained8 selectors under evaluator::colors_tests are budgets_match_detailed_full_and_fresh_across_weights_and_root_rebinding; budgets_preserve_supplied_contrary_influence_and_lazy_selection; budgets_preserve_zero_group_replacement_order_and_reset; budgets_preserve_full_identity_collision_and_fresh_cache_bypass; persistent_worker_crosses_repeated_search_stop_retry_and_budget_changes; positive_total_requests_saturate_without_changing_cache_or_evaluation; search_and_session_expose_requested_and_configured_budgets; affinity_cap_queries_before_mutation_and_preserves_active_cache_on_failure.

focused.json selects29 worker +8 ordinary-owner +3 scope controls,40 total. No build, test, engine/native execution or Git operation was performed during this source task.

Initial native preparation found an adapted test confusing a sparse epoch with a request count. The test-only repair and failed source/input/receipt preservation are recorded in [preparation-repair.md](preparation-repair.md). Production source is unchanged; the original clock and completed worker29 receipt are retained.
