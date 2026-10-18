#!/usr/bin/env python3
"""Combine independently measured pure kernels, preserving Root production."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

PREP = Path(__file__).resolve().parent
ROOT = PREP.parents[1]
TARGET = Path('/tmp/imp2-eval-kernels-combined-20261018')
RELATIONS = Path('/tmp/imp2-relation-states-bitplanes-20261018')
GROUPS = Path('/tmp/imp2-influence-groups-20261018')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sources(root):
    return {str(p.relative_to(root)):sha(p.read_bytes()) for p in
            [root/'Cargo.toml', root/'Cargo.lock', *sorted((root/'src').rglob('*.rs'))]}


def main():
    baseline = sources(ROOT)
    assert baseline == json.loads((ROOT/'evidence/production-bitplanes-use-build-20261018/receipt.json').read_text())['source_sha256_before']
    inputs = {}
    for source, receipt, pilot, ratio in [
        (RELATIONS, 'pgo-relation-states-use-build-20261018', 'pgo-relation-states-cpu-pilot-20261018', 'states_to_baseline'),
        (GROUPS, 'influence-groups-build-20261018', 'influence-groups-cpu-pilot-20261018', 'groups_to_baseline'),
    ]:
        build_path = ROOT/'evidence'/receipt/'receipt.json'
        pilot_path = ROOT/'evidence'/pilot/'analysis.json'
        build = json.loads(build_path.read_text())
        analysis = json.loads(pilot_path.read_text())
        assert sources(source) == build['source_sha256_before'] == build['source_sha256_after']
        assert analysis['complete'] and analysis['lifetimes_independently_reconciled'] == 60 and analysis[ratio] < 1
        assert json.loads((pilot_path.parent/'driver-terminal.json').read_text())['exit_code'] == 0
        inputs.update({str(p):sha(p.read_bytes()) for p in [build_path, pilot_path, pilot_path.parent/'driver-terminal.json']})
    TARGET.mkdir()
    for name in ['Cargo.toml', 'Cargo.lock']:
        shutil.copy2(ROOT/name, TARGET/name)
    shutil.copytree(ROOT/'src', TARGET/'src')
    shutil.copytree(ROOT/'tools', TARGET/'tools', ignore=shutil.ignore_patterns('__pycache__'))
    table = RELATIONS/'src/relation_table.rs'
    group = GROUPS/'src/influence.rs'
    relation = RELATIONS/'src/influence.rs'
    for p in [table, group, relation]:
        inputs[str(p)] = sha(p.read_bytes())
    shutil.copy2(table, TARGET/'src/relation_table.rs')
    text = group.read_text()
    start = text.index('#[inline]\nfn least_tier(')
    end = text.index('/// Exclude from normalized own support', start)
    relation_text = relation.read_text()
    begin_relation = relation_text.index('/// Classify the same four tested-piece tiers')
    end_relation = relation_text.index('/// Exclude from normalized own support', begin_relation)
    (TARGET/'src/influence.rs').write_text(text[:start] + relation_text[begin_relation:end_relation] + text[end:])
    lib = TARGET/'src/lib.rs'
    text = lib.read_text()
    assert text.count('pub mod influence;') == 1
    lib.write_text(text.replace('pub mod influence;', 'pub mod influence;\nmod relation_table;'))
    before_format = sources(TARGET)
    command = ['rustfmt', '--config', 'skip_children=true', *map(str, [TARGET/'src/influence.rs', TARGET/'src/relation_table.rs', lib])]
    with (PREP/'format.stdout').open('xb') as out, (PREP/'format.stderr').open('xb') as err:
        formatted = subprocess.run(command, stdout=out, stderr=err)
    assert formatted.returncode == 0
    assert sources(ROOT) == baseline
    after = sources(TARGET)
    archive = PREP/'prepared-source.tar.gz'
    files = {str(p.relative_to(TARGET)):sha(p.read_bytes()) for p in
             [*sorted((TARGET/'src').rglob('*.rs')), *sorted((TARGET/'tools').rglob('*')), TARGET/'Cargo.toml', TARGET/'Cargo.lock'] if p.is_file()}
    with archive.open('xb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode='w') as output:
                for name in sorted(files):
                    data = (TARGET/name).read_bytes()
                    member = tarfile.TarInfo(name)
                    member.size, member.mode = len(data), 0o644
                    output.addfile(member, io.BytesIO(data))
    with tarfile.open(archive, 'r:gz') as check:
        assert {m.name:sha(check.extractfile(m).read()) for m in check} == files
    result = dict(status='Combined source preparation only; no combined benefit/conformance claim', path=str(TARGET),
                  baseline_source_sha256=baseline, source_before_format=before_format, variant_source_sha256=after,
                  modified_existing_files=[name for name in baseline if after[name] != baseline[name]],
                  prototype_inputs_sha256=inputs, generator_sha256=sha(Path(__file__).read_bytes()),
                  format_command=command, format_returncode=formatted.returncode, archive=archive.name,
                  archive_sha256=sha(archive.read_bytes()), archive_files=files, planned_native_tests=134,
                  scope='Combine pure relation lookup and typed-list influence enumeration; Position/Node/ownership/R charges unchanged. Own PGO training, regression and matched baseline/table/combined comparison required.')
    with (PREP/'prepared.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k:result[k] for k in ['status', 'path', 'modified_existing_files', 'archive_sha256']}))


if __name__ == '__main__':
    main()
