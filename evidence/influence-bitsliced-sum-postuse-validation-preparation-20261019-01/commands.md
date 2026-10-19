Commands are documentation only; nothing below has run.

After parent reviews the exact plan and writes matching execution-clearance.json:

```sh
taskset -c 0-5,8-13 env PATH=/usr/bin:/bin TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/influence-bitsliced-sum-postuse-validation-preparation-20261019-01/run.py
```

Observe that actual outer tool terminal. Preserve any failure and stop. On successful actual completion, parent records actual_tool_terminal_observed=true, observed exit_code=0 and the real terminal_chunk_id (session_id only if one existed) at:

`/home/legolas/rook2/evidence/influence-bitsliced-sum-postuse-validation-20261019-01/tool-terminal.json`

Then, separately, offline reconciliation only:

```sh
taskset -c 0-5,8-13 env PATH=/usr/bin:/bin TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/influence-bitsliced-sum-postuse-validation-preparation-20261019-01/recheck.py
```

Observe and record its real outer terminal independently. Expected fresh products are output/profile-all.{stdout,stderr,child-terminal.json}, wire-driver counterparts, wire/receipt.json and8 raw fixture directories, identity.json; then preparation/recheck-original54.{stdout,stderr}, recheck-original54-terminal.json, recheck-original54-result.json, recheck-result.json. No native/search is launched by the offline recheck. Both helpers retain failure.json/recheck-failure.json respectively and refuse existing result-file overwrites.
