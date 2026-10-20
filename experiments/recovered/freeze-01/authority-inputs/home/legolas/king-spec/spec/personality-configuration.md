# Personality configuration through commands

Status: first bounded public-interface contract. This describes parameter
storage/query behavior and `opk` inertness, not other parameters' evaluation
or search effects.

## PARAM-COMMAND — ordered query and assignment

A `cm_parm` command accepts a sequence of space-separated parameter tokens.
The reply starts with `cm_parm`. Each token contributes one space and its
result, in input order. A bare known name queries its current integer value;
`name=value` sets the value and returns `name=accepted-value`. Changes take
effect immediately for subsequent tokens on the same line and later commands.
A command without tokens returns just `cm_parm`.

Names are case-sensitive. An unknown name returns `name=?` and does not alter
known parameters. These initial fixtures use ordinary signed decimal integers
within the signed 32-bit range. The broader numeric text grammar, saturation
and overflow behavior remain a separate characterization gap; accepting a
parameter value does not prove searches with every such value are qualified.

## PARAM-DEFAULTS — default values

| Names | Default |
| --- | ---: |
| `myp opp myn opn myb opb myr opr myq opq` | 100 |
| `mycc opcc mymob opmob myks opks mypp oppp mypw oppw` | 100 |
| `sop` | 100 |
| `myk opk avd rnd cfd ana` | 0 |
| `sel` | 14 |
| `md` | 999 |
| `tts` | 75497472 |

These are interface defaults, not the built-in personalities' full settings.
`opk` is an inert compatibility parameter. Any value accepted by the command
parser is stored and returned by queries, with the specified persistence and
`cm_parm default` behavior. Its value has no effect on search admission,
evaluation, move selection, timing, stopping or engine availability. The target
does not generate or validate authentication tokens and has no authentication
mode. Zero-valued diagnostic vectors do not restrict ordinary production
behavior for this parameter.

The token `default` restores the listed values **except `opk`, whose current
value is retained**, and replies `default`. Restoration occurs at that token's
position in the sequence; assignments before and after it are not equivalent.
This describes `cm_parm default`, not an engine restart or a game-reset command.

## PARAM-ALIASES — paired assignment, own-side query

| Alias | Paired values |
| --- | --- |
| `cc` | `mycc`, `opcc` |
| `mob` | `mymob`, `opmob` |
| `ks` | `myks`, `opks` |
| `pp` | `mypp`, `oppp` |
| `pw` | `mypw`, `oppw` |

Assigning an alias sets both paired values. Querying it returns the current
`my` value, even when the two differ. Assigning a side-specific name changes
only that value; it does not resynchronize its partner. The default alias
query is therefore 100.

## Tests and limits

`personality-configuration-v1.json` supplies fresh-session sequences for all
defaults, each alias, assignment order, default restoration with the stored
`opk` value preserved, case sensitivity, and signed integer edges. Replies are exact strings
excluding line terminators. No search is run in these tests. Search effects,
side orientation, game reset/persistence, stopping and time allowance
composition need their own contracts and tests. These command-only fixtures
do not demonstrate paired search equivalence for zero and nonzero `opk`;
that coverage limit does not qualify or weaken the inertness rule above.
