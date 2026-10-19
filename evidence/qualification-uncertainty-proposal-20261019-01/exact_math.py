"""Tiny exact analytical budget/error arithmetic; no observations or engine imports."""
from fractions import Fraction
import json

def q(x):
    return {"fraction": str(x), "decimal": float(x)}

initial = 132 * Fraction(2, 2**13)
followup = 132 * Fraction(2 * (1 + 19), 2**19)
assert initial + followup == Fraction(693, 16384)
r = {
    "status": "UNADOPTED analytical draft; no run evaluated",
    "median_parameters": 132,
    "initial_measured_per_parameter": 13,
    "final_measured_per_parameter": 19,
    "initial_family_miss_upper": q(initial),
    "followup_family_miss_upper": q(followup),
    "two_look_family_miss_upper": q(initial + followup),
    "two_look_joint_coverage_lower": q(1 - initial - followup),
    "initial": {"measured": 132*13, "warmups": 132, "lifetimes": 132*14},
    "both_collections_followed": {"measured": 132*19, "warmups": 132*2, "lifetimes": 132*21},
    "followup_additional": {"measured": 132*6, "warmups": 132, "lifetimes": 132*7},
    "search_collection": {"initial_lifetimes": 54*2*14, "max_lifetimes": 54*2*21},
    "game_collection": {"initial_lifetimes": 12*2*14, "max_lifetimes": 12*2*21,
        "initial_logical_searches_including_warmups": 632*2*14,
        "max_logical_searches_including_warmups": 632*2*21,
        "initial_measured_logical_searches": 632*2*13,
        "max_measured_logical_searches": 632*2*19},
    "unselected_single_warmup_alternative_max_lifetimes": 132*20,
    "lifetime_multipliers_vs_matched_one_warmup_three_measured_schedule": {
        "initial": q(Fraction(14,4)), "maximum": q(Fraction(21,4))},
}
print(json.dumps(r, indent=2))
