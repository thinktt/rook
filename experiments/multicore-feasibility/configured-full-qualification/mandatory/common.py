"""Cold setup helpers for exact-source mandatory qualification; no native startup."""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SPEC = Path('/home/legolas/king-spec/conformance')
HELPERS = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
SOURCE_COMMIT = '66f35e440b2180d4d22c2bcd0e5a8c99c0f1185d'
ORDINARY_SHA = '8f26d39fd1a69bc8a3aa6da2c364b6ddb4b065bc585a27c7420ae994566f8b1b'
PRODUCTION = Path('/home/legolas/rook2-experiments/configured-full-20261024-01/production')
VERIFICATION = PRODUCTION.parent/'verification-lane'
OPTIONAL = {'output.analysisCandidateReport', 'search.analysisRootSequence'}
OLD = ROOT/'experiments/first-main-cutoff-correction'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def put(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False); stream.write('\n')


def inventory():
    files, excluded, ids, operations = [], [], set(), set()
    for path in sorted((SPEC/'fixtures').glob('*.json')):
        data = read(path)
        assert data['version'] == 1 and data['cases']
        ops = sorted({case['request']['operation'] for case in data['cases']})
        row = dict(path=str(path), sha256=sha(path), cases=len(data['cases']), operations=ops)
        if set(ops) & OPTIONAL:
            assert set(ops) <= OPTIONAL, 'mixed mandatory/optional file requires an explicit source-level selection design'
            excluded.append(row)
        else:
            files.append(row); operations.update(ops)
            for case in data['cases']:
                assert case['id'] not in ids; ids.add(case['id'])
    assert set(op for row in excluded for op in row['operations']) == OPTIONAL
    return dict(files=files, excludedOptionalFiles=excluded,
                mandatoryCases=len(ids), mandatoryOperations=sorted(operations),
                optionalOperations=sorted(OPTIONAL), inventoryBasis='current released fixtures; only README optional operations excluded')


def passed_tests(path):
    return re.findall(r'^test (\S+) \.\.\. ok$', Path(path).read_text(), re.M)


def executable(log):
    paths = re.findall(r'Running unittests [^\n]* \(([^()]+)\)', Path(log).read_text())
    assert len(paths) == 1
    result = Path(paths[0]); assert result.is_file()
    return result


def verify(plan):
    for path, digest in plan['pins'].items():
        assert sha(path) == digest, path
    for name, digest in plan['engineSource'].items():
        assert sha(Path(plan['worktree'])/name) == digest
        assert sha(Path(plan['engineArchive'])/name) == digest
        assert sha(Path(plan['repo'])/name) == digest
    for name, digest in plan['diagnosticSource'].items():
        assert sha(Path(plan['worktree'])/name) == digest
        assert sha(Path(plan['repo'])/name) == digest
    assert sha(plan['ordinaryImage']) == ORDINARY_SHA
