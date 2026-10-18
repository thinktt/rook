# Fixed-deadline owned cleanup control

A synthetic native child deliberately ignores SIGTERM under the actual wait4
supervisor. The collector's forced-cleanup path reconciled the comparator,
supervisor and native PIDs in4.011s, within its fixed5s deadline. SIGKILL exit
is expected for this negative control. The complete driver/controller/native
source, command, before/after hashes, original output and PID observations are
retained. There is no successful native accounting receipt for the killed
supervisor, and none is asserted. This control is not an engine timing sample.
