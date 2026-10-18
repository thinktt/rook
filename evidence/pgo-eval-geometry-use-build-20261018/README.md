# Compiler stage for shared evaluation geometry

The exact source/tool archive and build receipt identify instrumentation versus
profile-use, compiler/target settings and immutable inputs. The source archive
matches the generic geometry prototype byte-for-byte; build flags and locations
have their own receipts. Instrumented executables are not timing artifacts.

Production PGO artifact
`1dc996b2a78854f7138142eff62cbc16cbbbb051ab9f0b8d74ea0b82d6584a89`
passes all54 strict replays and eight wire interruption fixtures. Its compiler
profile comes from `../pgo-eval-geometry-training-20261018/`. The separate six-case
PGO pilot supports retaining this source change, with no full-reference or
full-gameplay acceptance claim. See its own pilot directory for every sample.
