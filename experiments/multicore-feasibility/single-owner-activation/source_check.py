"""Bounded source-only numerical/transport preservation check; starts no process.

This deliberately makes no dispatch/complete/activation equivalence claim: those
contracts change, and their caller ordering and unwind proof require review.
"""
from pathlib import Path
import hashlib
import json
import re

CONTROL = Path('/home/legolas/rook2-experiments/workspaces/writer-regions-20261026-01')
CANDIDATE = Path('/home/legolas/rook2-experiments/workspaces/single-owner-20261028-01')
NUMERICAL = [
    'src/activity.rs', 'src/attacks.rs', 'src/endgame.rs', 'src/eval_basis.rs',
    'src/evaluation.rs', 'src/geometry.rs', 'src/influence.rs', 'src/influence/coherent.rs',
    'src/movegen.rs', 'src/pawn_progress.rs', 'src/pawn_structure.rs', 'src/pawn_terms.rs',
    'src/positional_terms.rs', 'src/relation_table.rs', 'src/shelter.rs',
    'src/tactical.rs', 'src/tactical/check_masks.rs',
]
FUNCTIONS = ['compute_input', 'signal_completion', 'wait_completion', 'both_done']
TYPES = ['Packet', 'SideOutput', 'Metadata', 'Metric', 'Readiness']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def extract(text, name):
    match = re.search(r'^([ ]{0,4})(?:(?:pub\(crate\)|unsafe) )?fn '+name+r'\b', text, re.M)
    assert match, name
    first = text[match.start():].splitlines()[0]
    if first.rstrip().endswith('}'):
        return first
    end = re.search(r'^'+match[1]+r'}$', text[match.end():], re.M)
    assert end, name
    return text[match.start():match.end()+end.end()]


def check(control=CONTROL, candidate=CANDIDATE):
    control, candidate = Path(control), Path(candidate)
    numerical = {}
    for name in NUMERICAL:
        before, after = (control/name).read_bytes(), (candidate/name).read_bytes()
        assert before == after, name
        numerical[name] = digest(before)
    before = (control/'src/colors_worker.rs').read_text()
    after = (candidate/'src/colors_worker.rs').read_text()
    functions = {}
    for name in FUNCTIONS:
        original, changed = extract(before, name), extract(after, name)
        assert original == changed, name
        functions[name] = digest(original.encode())
    types = {}
    for name in TYPES:
        pattern = r'^(?:struct|enum) '+name+r'\b[\s\S]*?^}'
        original, changed = re.search(pattern, before, re.M), re.search(pattern, after, re.M)
        assert original and changed and original[0] == changed[0], name
        types[name] = digest(original[0].encode())
    assert 'fence(Ordering::SeqCst)' not in after
    assert before.count('unsafe impl Sync') == after.count('unsafe impl Sync') == 1
    assert re.search(r'unsafe impl Sync for Cells\b', after)
    # Compare the shared numerical streams, excluding the intentionally changed
    # activation boundary. Scalar field projections become owned prefix fields;
    # this does not certify activation/failure code or compiler equivalence.
    old = extract((control/'src/evaluator.rs').read_text(), 'full_impl_prepare')
    evaluator = (candidate/'src/evaluator.rs').read_text()
    prefix, suffix = extract(evaluator, 'full_prefix'), extract(evaluator, 'full_suffix')
    def normalized(value):
        return re.sub(r'\s+', '', '\n'.join(line for line in value.splitlines()
            if not line.lstrip().startswith('//')))
    old_prefix = old[old.index('let colors_token'):old.index('Self::finish_full_worker_scope(call_scope);')]
    new_prefix = prefix[prefix.index('let colors_token'):prefix.rindex('        FullPrefix {')]
    assert normalized(old_prefix) == normalized(new_prefix), 'numerical prefix stream'
    old_suffix = old[old.index('let activity = chain.activity;'):]
    projections = {'pawn.relation_queries':'pawn_queries', 'selected.reused':'pawn_reused',
        'central.weighted':'central', 'patterns.bishop_coordination':'bishops', 'patterns.opening':'patterns'}
    for field, local in projections.items():
        old_suffix = old_suffix.replace(field, local)
    for field in ['central', 'bishops', 'patterns']:
        old_suffix = re.sub(r'\b'+field+r'\s*:\s*'+field+r'\s*,', field+',', old_suffix)
    new_suffix = suffix[suffix.index('let activity = chain.activity;'):]
    assert normalized(old_suffix) == normalized(new_suffix), 'numerical suffix stream'
    returned = prefix[prefix.rindex('        FullPrefix {'):]
    for expression in ['central: central.weighted', 'bishops: patterns.bishop_coordination',
                       'patterns: patterns.opening', 'pawn_queries: pawn.relation_queries',
                       'pawn_reused: selected.reused']:
        assert normalized(expression) in normalized(returned), expression
    return dict(unchangedNumericalSourceSha256=numerical,
        identicalWorkerFunctionSha256=functions, identicalWorkerTypeSha256=types,
        numericalPrefixStreamSha256=digest(normalized(old_prefix).encode()),
        numericalSuffixStreamSha256=digest(normalized(old_suffix).encode()),
        ownedPrefixScalarProjections=projections,
        originalRmwProtocol=True, narrowCellsSyncCount=1,
        scope='selected unchanged kernels and transport operations only; changed owner/activation/failure paths require separate reviewed proof and focused native controls')


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
