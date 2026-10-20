# Root-window reachability: stronger conditional path, native witness still open

No actual native collapsed-window counterexample is established. The positive-saturation proposal at best=8999 fails. A canonical START negative-saturation chain is materially stronger than the old supplied-component examples, but actual restricted-iteration entry and later return-band correlation remain unproved. This review performs no engine/test/model/build execution and selects no runtime witness or repair.

## Actual root and seed ownership

Current57 source owners in input-pins.json equal frozen W57, source74 b845e921. Session binds effective parameters and passes stored rnd as u32 (session.rs:450–472); parameters.rs:112 rejects negative rnd, not large positive i32 values. Actual timed entry validates rnd<=i32::MAX and iteration count1..62 (timed.rs:511–514), prepares the root and clears owned search work before drive (517–543). The root is not an arbitrary supplied score/counter component.

Actual WireHost ignores the supplied seed, sampling POSIX seconds as u32 and adding entry with wrapping arithmetic (bin/rook2.rs:18–26; host.rs:11–13). A fresh Session's first go has entry0; persistent prior work can change entry. Acquisition is once before drive, not per move/iteration/retry (timed.rs:536–552). Thus Session::new(seed0) or a system_seconds argument alone does not prove seed0 on ordinary CLI. An explicit diagnostic override is separate. No actual seed was sampled here.

The move mixer uses T(s)=s XOR(s<<13 mod2^32) XOR(s>>7), then move contributions, modulo R+1 and minus floor(R/2) (timed.rs:216–244; root-randomization.md:34–59). Calendar seconds cannot be substituted directly for T(s).

## Positive saturation is not the proposed witness

A(s,d) preserves |s|>=9000 and otherwise clamps to[-8999,8999] (timed.rs:193–198; root-randomization.md:64–77). At B=P=8999, aspiration is[8999,9000], not[8999,8999]: the increment creates9000 before A is applied. For any adjustment the9000 endpoint remains9000 and the ordinary endpoint remains<=8999, so this pair stays strict after exchange/negation. Restricted fail-low tail ranking may produce8997 from8999 but does not lower an existing best8999 (root_schedule.rs:156–164). Actual B8997/8998 with P<=8998 can collapse, but its native score correlation is not established by clamping to8999.

## A canonical conditional negative chain

Let B=2^29. In START all20 legal root moves are ordinary, from rank1/2. Source weight<=18 and destination weight<=38 imply both move-only contributions are<B; their XOR is<B. With seed0 and R=i32::MAX, K<B and adjustment=K−(2^30−1), hence adjustment<=−2^29. Every ordinary-band raw root return then saturates to−8999.

Depth1 is a real source base case, not a supplied child answer: its first child request is depth0 and hands to Q; each START opening child is unchecked, has no tactical capture/direct-check move for the opposing side, and has ordinary standing return (Q's endgame finish clips scores to±7900; quiescence.rs:267–293 and continuation, endgame.rs:535–577). Protected root endpoints±10000 remain unchanged. Thus all normally completed depth1 root rankings become−8999 under this seed/rnd condition. This base case does not prove later searches remain ordinary-band or accumulate25000 nodes.

There is also a natural-seed *conditional class*, not a measured witness. For a fresh entry0, suppose acquired seconds s is in[3B,4B) and bits18..16 are zero. T(s)'s upper 3-bit block is3: (s>>7) has no bits29..31 and (s<<13)'s block is bits18..16. XOR with opening move contributions<B preserves block3. Choose admitted R=3B−1=1610612735. Then K in[3B,4B), K mod(R+1) in[0,B), and adjustment in[−3B/2+1,−B/2], so adjustment<=−2^28. The same ordinary-return saturation follows. Bare seconds block3 is insufficient; persistent entry may change s. This is a wall-second class description, not a claim about an acquired current seed.

Now conditionally suppose a later iteration actually enters Restricted, previous best<=8998, and its first candidate returns in the ordinary band under one of these all-negative adjustments. First requested window is always[-10000,10000]; its adjusted ranking is−8999. With previous=−8999, the next aspiration is[−8997,−8996]. Subtracting the next large negative adjustment clamps both to8999; the actual child request becomes[-8999,-8999] (timed.rs:619–628). More generally any previous<=8998 keeps that upper endpoint ordinary and the same saturation conclusion applies. This is an exact implication on actual caller formulas, not an actual completed search trace.

## Missing premise and bounded discriminator

Restricted policy is fixed from actual cumulative N>=25000 at *iteration entry* (root_schedule.rs:21–26,82–98; timed_sequence.rs:38–41). Crossing25000 during an unrestricted iteration only selects its EasyIteration adjustment; another iteration must actually start (75–82). Neither supplied initialSearchId nor controlled child work proves this native event. Seeded/fixed components and arbitrary Session seeds do not close natural CLI acquisition.

The source does not presently prove START with these parameters reaches a restricted entry before a time/depth/stop/mate-band exit, nor that the relevant first return and previous score remain in the ordinary band. Mate-band raw returns are preserved by A and break a blanket saturation induction. Negative−8999 itself is not excluded by the stop checks: losingBestScore requires<=−9000 and mate-bound termination is near−10000 (timing.rs:169–177,207–215); actual clock/budget and tree behavior still matter. Large randomness therefore does not by itself discharge either missing premise.

A future finite discriminator, if separately selected, needs one actual canonical-position native search with its acquired seed and admitted settings, actual iteration-entry N/policy, previous/best and returned raw-score band, and requested windows. Exact move/seed algebra can reconstruct transformed endpoints; no supplied child answers or fabricated work should substitute for these observations. Existing diagnostic root Step/Pass records observe requested windows, while actual seed logging is a separate explicit CLI diagnostic facility. This memo does not authorize a run, instrumentation, timing experiment, widening, clamp, cap, or fallback.

Released root-aspiration.md:42–52 and restricted-root-sequence.md:46–63 explicitly describe controlled contexts; root-randomization.md:74–77 permits transformed collapse. Accordingly the remaining question is native composed reachability and its enclosing interpretation, not a contradiction established by a controlled numeric example. Keep the earlier conditional L<U recursive proof and the unresolved composed-domain/hint questions separate.
