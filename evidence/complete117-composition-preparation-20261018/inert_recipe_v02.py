"""INERT source-text recipe. Importing does no I/O; direct execution always stops.
No authority to compose, copy, hash, archive, inventory, parse Rust, or validate.
Future caller must first obtain parent clearance and bind accepted corrected111 test source.
Closed Go source/review is resolved; original111 failure remains preserved.
"""

ORIGINAL_FAILED111 = "/home/legolas/rook2-work/imp2-generic-joined111-proposal-20261018-1ff1ef1f"
ORIGINAL111_GRAPH_FROM_BOUND_METADATA = "dd5c8b5fce2952510c80dfb129ab46f5e7cc56f520610f8e531858a26e6beb49"
COUPLED112 = "/home/legolas/rook2-work/imp2-coupled-timed112-proposal-20261018-ve4rftiq"
PERSISTENT_REV02 = "/home/legolas/rook2-work/imp2-persistent-session113-revision02-20261018-idpvozjm"
GO_CLOSED_SOURCE = "/home/legolas/rook2-work/imp2-go-outcome-revision-20261018-gejdcnbl"
GO_REVIEW = "/home/legolas/rook2/evidence/go-outcome-revision-score-context-review-20261018/review.md"
SELECTED_CORRECTED111_SOURCE = None  # Must await fresh agent exact path/patch +parent acceptance.
ORDINARY_TEST_ONLY_OWNER = "src/ordinary.rs"
REQUIRED_TEST_BASIS = "maximum_depth2 actual-Q tail witness; production ordinary body unchanged"
DEFAULT_CODEGEN_CONTROL = "validated10917e75; full existing artifact identity must be bound later"
OPTIONAL_FAILED_CODEGEN_CONTROL = "111efe541 FAILED unit basis only; no qualification transfer"

# Remaining filenames come from exact111's known manifest only after clearance.
NATIVE_COUPLED_OWNERS = (
    "src/engine.rs", "src/lib.rs", "src/timed.rs", "src/timed_sequence.rs",
    "src/timing.rs", "src/work_clock.rs",
)
NATIVE_SEED_OWNERS = ("src/host.rs", "src/session.rs", "src/bin/rook2.rs")
COLD_ADDITIONS = {
    "diagnostic/src/controlled_timed.rs": COUPLED112,
    "diagnostic/src/persistent_sessions.rs": PERSISTENT_REV02,
}
COLD_REPLACEMENT_PENDING_REVIEW = "diagnostic/src/actual_timed.rs"
MAIN = "diagnostic/src/main.rs"

# Disjoint anchors make the two additions independently commute. Each must
# reconstruct its reviewed parent main from that parent's own original base.
CONTROLLED_MAIN_EDITS = (
    ("mod controlled_root;\n", "mod controlled_timed;\n"),
    ('        "search.genericTimedSearch" => generic_timed::dispatch(input),\n',
     '        "search.timedRootSequence" | "search.workTimedRootSequence" => controlled_timed::dispatch(operation,input),\n'),
)
PERSISTENT_MAIN_EDITS = (
    ("mod post_captures;\n", "mod persistent_sessions;\n"),
    ("    match operation {\n",
     '        "session.searches" | "session.clockSeededSearches" | "session.interruptedSearches" | "session.ordinaryIterations" => persistent_sessions::dispatch(operation,input),\n'),
)

def add_exact(text, edits):
    """Pure text transformation only; not invoked by this inert plan."""
    for anchor, addition in edits:
        if text.count(anchor) != 1 or addition in text:
            raise ValueError("unreviewed/duplicate main anchor or addition")
        text = text.replace(anchor, anchor + addition, 1)
    return text

def remove_exact(text, edits):
    """Pure inverse; every original context must still be present exactly once."""
    for anchor, addition in reversed(edits):
        joined = anchor + addition
        if text.count(joined) != 1:
            raise ValueError("main inverse has lost its exact reviewed context")
        text = text.replace(joined, anchor, 1)
    return text

def future_main_proofs(base, coupled_base, coupled_parent, persistent_base, persistent_parent):
    """Returns proposed TEXT after required proofs; no file mutation or invocation."""
    if add_exact(coupled_base, CONTROLLED_MAIN_EDITS) != coupled_parent:
        raise ValueError("coupled parent's main is not its reviewed additive delta")
    if add_exact(persistent_base, PERSISTENT_MAIN_EDITS) != persistent_parent:
        raise ValueError("persistent parent's main is not its reviewed additive delta")
    first = add_exact(add_exact(base, CONTROLLED_MAIN_EDITS), PERSISTENT_MAIN_EDITS)
    second = add_exact(add_exact(base, PERSISTENT_MAIN_EDITS), CONTROLLED_MAIN_EDITS)
    if first != second:
        raise ValueError("main additions do not commute")
    if remove_exact(remove_exact(first, PERSISTENT_MAIN_EDITS), CONTROLLED_MAIN_EDITS) != base:
        raise ValueError("main inverse does not reconstruct exact111")
    if remove_exact(remove_exact(second, CONTROLLED_MAIN_EDITS), PERSISTENT_MAIN_EDITS) != base:
        raise ValueError("reverse main inverse does not reconstruct exact111")
    return first

if __name__ == "__main__":
    raise SystemExit("INERT PLAN ONLY: accepted NEW111 test-only source and explicit parent composition clearance required; no operations performed")
