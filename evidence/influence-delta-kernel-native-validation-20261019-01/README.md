# Experiment29 isolated kernel validation

Source70 a8ab72ed… passes179 native tests (177 library+2 dev), including the new all128-byte independent-oracle comparison:94 adversarial transitions and122 deterministic legal ordinary transitions,61 per color,33 captures/89 quiets. Frozen test-image identities, first execution records and stable source/input checks are in result.json; actual driver379dc8/session9650 completed bcce89/0. No default engine, search integration, timing or PMU run occurred.

Raw test JSON and independently recomputed rows are retained. Legal sample fresh construction made9548 byte writes/3012 ray entries; delta made2327/768, plus976 discovery queries/234 selected origin-directions and15616 logically scheduled copy bytes. Writes decreased for all122 pairs; ray entries decreased104, tied17, increased1. These are operation counts in selected legal transitions, not machine instructions, actual copy traffic, production demand/eligibility or measured CPU saving. All6 mover kinds occurred. This is enough to justify one narrowly scoped ordinary-search integration and matched timing, not adoption.

Parent review and kernel/source endpoints remain separate immutable evidence. Production candidate25 is unchanged; rejected26/27/28 are not composed.
