# Simulated-instruction diagnostic

An independently downloaded public Debian Valgrind3.24.0 package was extracted
locally without system installation. `provenance.json` binds the package and
actual tool binaries and records the launch. The unchanged released profile-01
replay comparator passed against frozen baseline ordinary artifact
`da82041f29091ed8db54f2cd2ffd0c338da5ae5216cae3caea6130974573e648`.

Callgrind reported 20,083,250,913 `Ir` events, with cache and branch simulation
disabled. `Ir` counts simulated instructions; it is not hardware retired
instructions, CPU cycles, IPC, or native whole-search CPU time. The native
`find_attackers` instantiations appear in several inlined attribution rows and
account for roughly one-third of the simulated total. That includes attack uses
outside candidate legality and does not represent removable work.

`profile-01.callgrind` and the complete annotated table are retained, along with
the strict behavioral comparator result. See the upstream
[Callgrind manual](https://valgrind.org/docs/manual/cl-manual.html) for event
semantics. This run identifies an optimization candidate only.
