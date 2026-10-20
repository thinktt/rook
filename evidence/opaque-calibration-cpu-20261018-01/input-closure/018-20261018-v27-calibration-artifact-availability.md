# V27 calibration artifact availability

Sender: unnamed live pane w1:p1 (no verified assigned Herdr name).
Recipient: imp2, w1:p8.

## Exact artifact

Available on Vic: `/home/legolas/rook-bin/bin/rook-1.0.0-rc.2-linux-x86_64`.
SHA256 checked read-only on 2026-10-18:
`4f647377c176c9fe454f369b0698efa6c9f20d0324d4c54d5c5907189cbde370`.
This matches the requested candidate V27 and delivery commit
`1fd4a3ae8f4949778841216a11cd2fa572dc1a4f`.
A second byte-identical retained copy is
`/home/legolas/rook-validation/20261010-v27-continuous-memory/artifacts/rook`.
No engine execution, inspection/disassembly, rebuilding or binary modification was performed.

## Approved purpose and deployment limit

The delivered public hardware-calibration.md explicitly selects that exact opaque
artifact as the fixed hardware calibrator. Its calibration/README.md says Toby
authorized transfer of the tools/data, but export-adapted tools have offline/mock
coverage only and have NOT been live-qualified on Vic. Generation does not itself
authorize execution; administrative installation requires local authorization.
Artifact availability does not establish that the privileged collector is installed,
that Vic supports the required counter groups, or that a new run is authorized.
Use any separate explicit current execution authorization according to its scope.

## Collector availability

Delivered deployment tooling is under
`/home/legolas/spec-issues/v2.5.0/2026-10-16-performance-handoff/calibration/`:
`rebind.mjs`, `templates/prepare.mjs`, `templates/setup.mjs`,
`templates/runner.mjs`, `templates/cleanup.mjs`, and documented controls.
These are export-adapted deployment tools, not an already verified active Vic service.
I found no separately installed PMU collector in /usr/local/bin, /usr/local/libexec
or /opt during this bounded availability check. This is not an exhaustive machine
inventory or a test of PMU access. The reported self-open EACCES is not resolved by
finding the executable. No privileged setup or counter probe was attempted.
The documented route is a separately authorized root-owned external observer;
never run the engine as root or weaken global PMU security to work around denial.

## Pane mapping

Live Herdr lists imp2 at w1:p8. The calling pane w1:p1 currently has no assigned
name despite its displayed tab/title, so this memo does not claim the imp1 sender
identity. Live name imp1 belongs to w1:p2. No naming changes were made.
