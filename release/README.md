# Build, qualify, release

The pieces are separate and usable outside GitHub:

- `build.py` runs the pinned Docker builder and writes the four binaries/receipts.
- `qualification.json` records locally approved hashes, sizes and the checks
  those exact bytes passed. No executable is committed.
- `package.py` verifies all four bytes against that manifest before preparing
  versioned binary assets, `SHA256SUMS` and `release.json` provenance.
- `.github/workflows/release.yml` runs only for pushed `v…` tags. It builds,
  verifies, then calls `publish.sh`. Ordinary pushes do nothing automatically.

For a local release dry run, use fresh directories outside the repository:

```sh
python3 release/build.py --output /tmp/rook-build
python3 release/package.py --build-output /tmp/rook-build \
  --version v1.0.0 --output /tmp/rook-assets
(cd /tmp/rook-assets && sha256sum --check SHA256SUMS)
```

That does not create a tag or contact GitHub. Debug information and symbols are
retained in all binaries. The dynamic pair must match its recorded candidate
identities; static qualification is separate and does not inherit the original
main engine's external game-gate result. The manifest describes finite checks,
not a blanket claim of specification/performance acceptance.

On GitHub, publishing creates a draft, uploads the verified assets, then makes
it public. A failed upload leaves a draft that the same tag's rerun can complete.
An already published release is never overwritten by this workflow. Temporary
failures can be rerun; a code/workflow fix needs a tag on the corrected commit.
No workflow creates or moves tags. Authentication, repository permissions and
actual GitHub upload behavior require a first real GitHub run; local validation
does not claim to exercise those services.

## Local qualification and profile preparation

Testing is local in this version; there is no CI testing workflow. The optional
local supervisor requires a built builder image and an Alpine image containing
Python3 and Node. It uses only the separately supplied released specification:

```sh
python3 release/prepare.py --output /absolute/fresh/study \
  --builder-image rook-release-builder:local --alpine-image alpine-checks:local \
  --spec /absolute/path/to/king-spec
```

It runs one static instrumented build, all 54 standard training cases, profile
merge/text export, two clean four-binary builds, then the static pair's mandatory
fixtures and ordinary pre-gate. The latter includes standard54 correctness,
12 games, continuity, seed controls and interruption wire checks. There is no
full 3,288-game run. All native/checker processes use CPU14; leave CPU15 idle and
run the outer supervisor/build helpers on the housekeeping CPUs. Its generated
helper copies retain protocol behavior while changing only checker affinity.

Each stage has a deadline; the supervisor watches a 4 GiB artifact budget, stops
on failure without retry and removes its owned container on timeout. Optional
`--notify-pane`/`--notify-prefix` sends a completion/failure message through Herdr.
It updates the static profile and its recipe checksum, but leaves qualification
manifest approval to the implementation owner after receipt review.

Run non-native release controls separately:

```sh
python3 -m unittest discover -s release -p 'test_*.py' -v
actionlint .github/workflows/release.yml
```

These check hash-tamper rejection, complete artifact coverage, checksum output
and draft/upload/publication sequencing with a local fake GitHub CLI. They never
publish anything. Full local verification records are linked by the manifest.

## Current local verification

The current dynamic pair reproduces candidate68 exactly. Both variants reproduced
identically in two fresh builder containers, with debugging retained. The static
diagnostic passed 115 mandatory files / 7,673 cases. Its main companion passed
standard54, all 12 games / 632 searches / 5,801 posts, continuity, seed controls and
8 interruption sessions / 24 searches. No full game gate was run on the static
companion. The original dynamic qualification was reused by exact hash.

One inherited wire-helper fixture path failed during setup, before any wire
engine launch. The binding was corrected, only the missing wire checks and
collector were run, and the failed setup remains preserved. No completed native
request was retried. Short-child post-exec point observations were unavailable
for some diagnostic/seed requests; all direct exec/wait chains and checker
outcomes are recorded. These finite observations are not a continuous ownership
or final performance qualification claim.

[local-verification.json](local-verification.json) records local checks and
raw-receipt hashes; [qualification.json](qualification.json) lists all four
artifact identities and their qualification scope. No tag, GitHub Release or
external artifact transfer has been made by this work.
