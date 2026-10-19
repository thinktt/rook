# Exact expected process contract

Released ordinary-play-ingress.md:65–88 expressly admits `8/8/8/3Pk3/8/8/8/K7 w - e6 0 1`, then d5e6, retaining the White pawn on e6 and no Black king. In force mode: no move/post/checkmate/stalemate/result. Immediately following ordinary go: exit1, no signal, no move/post/result and no further command processing. This is not an empty-candidate completed search. ordinary-xboard-wire.md:213–217 binds the same fatal rule.

Exact normal CLI input is stdin.expected.raw: xboard, force, that setboard, d5e6, go. All five commands are silent in this sequence. stdout and stderr must each be EXACT zero bytes; native exit must be code1/signalNone. No trimming, ignored seed notice, omitted echo, arbitrary timeout substitute or quit/EOF success. No --diagnostic-seed-command, no work-clock flags and no extra native lifetime.

Own frozen40 source: Session coordinate243–260 produces the exact cold transition and resultNone; prepare_go436–438 returns FatalKingVictim before root/seed/search; bin/rook2.rs56–60 and121–127 map it to silent ExitCode1. Earlier invalid setup/errors would be Message stderr, illegal d5e6 would emit stdout, and abrupt termination signals fail. The source facts justify the expected bytes but DO NOT themselves establish an actual process observation. The previously passing native Session test likewise is not counted as this process witness.

The parent must separately authorize execution after48 closes. This preparation launches nothing, and no process PASS is claimed.
