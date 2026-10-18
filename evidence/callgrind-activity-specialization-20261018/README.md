# Activity-specialized canonical instruction simulation

Frozen canonical `8d9dddc5` passes the unchanged strict profile-01 replay under
Callgrind 3.24.0, with normal engine exit. Whole-lifetime simulated Ir is
**11,603,840,314**, versus previous `8c4619a7` **12,027,315,634**: ratio
**0.9647905374**, or **3.520946% fewer**. This is simulated user instruction work;
it supplies no retired-instruction, cycle, CPI/IPC or native timing claim.

The driver binds the exact binary, native43 source snapshot, original streams,
released oracle/workload, public Valgrind tools and complete profile/annotations
in [provenance.json](provenance.json). The actual successful tool terminal is
retained separately. [reconcile.py](reconcile.py) independently checks those
original bytes and the archived build sources; later working-tree edits do not
change the source attributed by this run.

The largest exclusive source row is activity compute: 1,162,651,588 (10.02%).
Legal replies, full generation, influence construction and tactical generation
remain substantial. Source labels include compiler inlining; these rows are
not independent function totals. The full annotations and raw Callgrind file
remain available. Changes in profile and inlining prevent assigning every
historical source-row difference to one kernel.

The engine ran on CPU14; helpers ran on 0–5,8–13, with sibling15 reserved idle.
No owned build, test, other engine collection or profiler overlapped the run.
This diagnostic guides further experiments and does not close qualification.
