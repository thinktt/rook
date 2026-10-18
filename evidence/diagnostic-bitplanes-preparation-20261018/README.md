# Same diagnostic frontend linked to integrated native source

The same29-operation frontend/source archive that passed against the old native
layout is rebuilt against the integrated160/176 native layout. Both native
source maps and all frontend/plan/verifier/fixture identities are bound before
and after. The canonical native instrumentation build is used solely to identify
the linked source closure; the diagnostic itself is a separate generic build.

The fresh adapter fab90bb7 passes25 unit tests and all1214 external cases,
covering23 complete fixture files plus the prior25 selected phase/identity
cases. The real unit executable and adapter are frozen and hashed; the build
source archive and actual reports are under `../diagnostic-bitplanes-20261018/`.
Prior4d07ce08/pre-integration and c4cd8566/27-operation evidence remains intact.
No complete mandatory or whole-production qualification follows from this subset.
