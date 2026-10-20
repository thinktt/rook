# Experiment27: pressure digit sums

Parked; candidate25 remains the retained production source and delivered own-PGO
image. The trial replaces only pure pressure_value arithmetic and adds one
exhaustive native test against the original formula. All 256 possible mark
values match. Traversal, masks, marks, semantic work and stored state are unchanged.

Generic candidate25 `2940ae5c` totals **14.1854385s** in seven case medians.
Experiment27 `59497f6d` totals **14.1524495s**, **0.232555% lower**. Four cases
are lower, below the fixed minimum five; aggregate gain is also below the fixed
0.5% minimum. Worst case ratio 1.003396 is below 1.02. All 70 native lifetimes
were completed: 14 excluded warmups and 56 measured samples. No retries or
outlier deletion. These are whole-native wait4 user+sys times, including startup
and the recorder's disclosed tiny Python pre-exec interval, not search-only
full54 figures from the delivered own-PGO image.

| Case | Candidate25 generic median(s) | Experiment27 generic median(s) | Lower by |
| --- | ---: | ---: | ---: |
| profile-01 | 1.0666075 | 1.0641790 | +0.228% |
| profile-02 | 0.7396770 | 0.7399450 | -0.036% |
| profile-04 | 4.5760520 | 4.5827855 | -0.147% |
| profile-05 | 2.5131470 | 2.4892075 | +0.953% |
| profile-29 | 0.2509035 | 0.2517555 | -0.340% |
| profile-35 | 4.6436415 | 4.6302585 | +0.288% |
| profile-08 | 0.3954100 | 0.3943185 | +0.276% |

All 70 original replay checks passed live and independently again offline; native
accounting, exact images, affinity, samples and decision reconcile. Actual pilot
34504:b4b1ee→d58d4d/0; independent reconciliation 79d043/0.

The trial passes 179 native tests (177 library, 2 dev), with test images copied
and hashed before their first execution. The 178 preexisting tests are unchanged.
Generic lowering removes four pressure multiplications per admitted ray value;
the pressure frame remains 88 bytes, with no new hot call or table. The static
change does not produce sufficient measured whole-search benefit.

The full117 suite, own-PGO training/use, full54 regression and eight-wire/24
interruption checks and 12-game pre-gate are intentionally not executed for this
failed development trial. Unused PGO preparation remains launch-false; its early
metadata-only filename assertion failure and corrected continuation are preserved.
No production source change, performance qualification or external run follows.
