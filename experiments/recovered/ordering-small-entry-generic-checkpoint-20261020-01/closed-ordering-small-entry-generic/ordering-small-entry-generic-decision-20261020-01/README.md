# Experiment55: park outer small-list entry

The actual compiler routes preferred<=6 directly to the unchanged public sorter and copy before the six-stream helper frame. Caller stack reservations remain unchanged; ordering code grows and large lists pay both outer and preserved inner guards. The avoided104B helper layer is relative to experiment54; production51 already sorts small lists directly.

Twelve focused tests pass. The unchanged one-shot generic fixed70 screen against51 reconciles all70fresh lifetimes and original replay checks: summed case medians13.5667655→13.524396CPU s, ratio0.9968769637832982,0.31230362167018466% lower,6/7lower, worst1.0021181806443953. The required aggregate ratio<=0.995 fails. Park without retry, PGO or adoption. No whole54/12gain is established. Production remains51.
