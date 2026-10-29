# Pre-map Activity geometry trial

Selected generic60+5 from design e8ef49f8; results pending. Exact source is an
isolated derivative, not adopted canonical source. Preserve c242/1a81/d71 and all
prior artifacts. [Plan](plan.md), [ownership argument](ownership-proof.md),
[policy](policy.json), and [source freeze](preparation.json) bind the finite lane.

Raw path: `/home/legolas/rook2-experiments/pre-map-geometry-20261029-01`.
Candidate source: `/home/legolas/rook2-experiments/workspaces/pre-map-geometry-20261029-01`.
Restore the source patch over single-owner69 with `git apply --unidiff-zero source.patch`.
The source patch includes focused tests, not binaries or raw data.

The first compile failed before any unit ran: the new cfgtest helper referenced
unavailable serde_json. Repair only its fixed report-field parser; production
bytes are unchanged. Exact initial tools/source/pipeline/stdout/stderr are kept
in the raw `repair-01/` archive and bound by preparation.json.

After the announced quiet window, the original `native.py prepare` was attempted.
Resume once with `native.py repair-prepare`, then `native.py collect`.
Both commands use the persisted original3600s clock. `close_pipeline.py --root RAW
--output RAW/closure-audit.json` independently binds terminal outputs. Tools watch
caps/failures; do not repeat completed native controls or requests. No timing,
qualification, PGO, adoption or delivery follows beyond this selected comparison.
