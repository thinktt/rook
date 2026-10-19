# Reject direct child construction at the backend gate

Retain candidate25. Experiment28 attempts to remove the intermediate Position
return copy by constructing a complete local child Node before applying the
same transition. Only Node::child changes; all 178 tests remain byte-identical.

Actual generic code retains both transfers and enlarges the second from 160 to
176 bytes. The child frame grows 16 bytes. Both ordinary and Q reach this owner.
The intended saving is absent, so no native tests or timing are run. No source
is promoted. This is a static mechanism rejection, not a measured CPU result.

See [the preserved decision](../../evidence/direct-child-construction-decision-20261019-01/README.md).
