# Exact analytical proof and selection limitation

Fix a parameter's finite lower population median `m`. It satisfies `P(X<m)<=1/2` and `P(X>m)<=1/2`. Closed interval endpoints matter: equality is covered. All probabilities below concern the declared measured CPU distribution, including its timer quantization, not an unobserved ideal unrounded CPU variable.

For13 iid measured samples, `m<X_(1)` requires all13 values strictly above `m`, while `m>X_(13)` requires all13 strictly below. Thus `P(m notin [X_(1),X_(13)]) <= 2/2^13`.

For19 iid samples, `m<X_(2)` requires at most one sample <=m. Since `P(X<=m)>=1/2`, its probability is bounded by the lower binomial tail `sum(k=0..1) choose(19,k)/2^19 = (1+19)/2^19`. Similarly `m>X_(18)` requires at most one sample >=m and has the same bound. Therefore `P(m notin [X_(2),X_(18)]) <= 2*(1+19)/2^19`. Atoms and ties only reduce these strict noncoverage probabilities; no continuous-distribution assumption is needed. Fixing a median functional avoids an ambiguous choice among nonunique medians after seeing results.

Define each parameter's potential19-sample stream before collection. The first interval uses its first13, and the second uses all19 if the collection is selected for followup. A union bound over132 parameters and both possible looks gives:

```
initial family error <= 132*2/8192 = 33/1024 = 0.0322265625
final family error   <= 132*40/524288 = 165/16384 = 0.01007080078125
any-look family error <= 693/16384 = 0.04229736328125
joint coverage >= 15691/16384 = 0.95770263671875
```

This is conservative: no independence across the132 streams or two looks is assumed. A selected-followup error is a subset of the corresponding potential final-look error, so deciding whether to collect the six extras from initial data does not enlarge the unconditional union bound. It does **not** follow that coverage conditional on the selected-inconclusive subset is >=95%. Nor is it valid to apply an ordinary fixed-look95% interval repeatedly and stop favorably. The fixed13/19 stream model requires the same distribution across both stages despite any intervening delay or warmup. If the stage changes that distribution, this proof has no identified common-median target.

On the event of simultaneous coverage, nonnegative numerator bounds and positive denominator bounds imply the individual and sum-ratio intervals by monotonicity of division. Hence every performance decision stated in proposal.md is supported by the same joint coverage event, including selection of a stopping look. No extra multiplicity cost is incurred merely by computing all those ratios from the already simultaneous rectangular median bounds. This does not validate systematic accounting bias, environment drift, the chosen reference or behavioral equivalence.

The probability arithmetic in exact-math.json is exact rational arithmetic. The binomial-tail step is the usual Bernoulli stochastic ordering at success probability>=1/2, justified by iid trials. Independence cannot be replaced by exchangeability alone: perfectly correlated slow/fast samples can make all13 fall on one side with probability1/2 instead of2^-13. We have not established iid/stationarity on any actual machine.
