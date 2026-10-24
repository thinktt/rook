# Configured FULL: Linux affinity cap and own-PGO comparison

At each thread-budget configuration, positive requests above1 query the calling
thread's permitted Linux affinity. Exactly one allowed CPU configures1, preserving
the requested number; otherwise configured capacity is at most2. Requested1
does not query. Invalid input/query failure leaves prior configuration intact.
`--threads=8 --inspect-threads` reports both numbers explicitly. No ordinary wire
banner, affinity widening, physical-core inference or reactive reconfiguration
after external placement occurs. Unsupported non-Linux multi-thread policy is
an explicit error; default1 does not require that query.

[Configuration closure](verification-proof.json):12 focused unit checks,13 CLI
controls and two exact original08 projections pass. With only CPU14 permitted,
both request1 and request2 observe one native task throughout sampled boundaries
and polls. Their whole-lifetime observations are0.3892s/0.3874s. These finite
observations remove the pathological sharing seen in the preserved
[55.61s prior control](../usable-full/report.md); they are not a repeated timing
campaign. Query failure is injected through the same setter's narrow query seam,
not induced in the OS. The worker protocol itself is unchanged from the prior
completed20-check practical-integration record.

Generic verification image SHA256:
`22c60b44e15f6ed2ed437bc9aaf74bd1a8fc9c8c8f47ea651b420d5f8fb8b593`.
Raw data:
`/home/legolas/rook2-experiments/configured-full-20261024-01/verification-lane/`.

The [selected plan](plan.md) separates configuration verification, fresh training
and production comparison. `verify_pipeline.py` drives the focused lane;
`verification_close.py` audits its saved results. `pipeline.py` builds one
instrumented image, trains original54 once per mode, merges once and builds an
own-PGO image before a64-life four-configuration comparison. It stops for an
evidence decision; a separately invoked `--stage full54` supplies the conditional
216-life extension only if selected. Training/measurement reconcilers execute no
engines. No broad conformance/gameplay gate, adoption or delivery is selected.
