"""Bounded static capture of two already frozen own generic engine images."""
from pathlib import Path
import hashlib
import json
import os
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SIDES = {
    'control': ('activity-value-inputs-generic-build-20261018-01',
                '7cf3980014506970ba8aaf885bcc1c983823307005aaae7efc5d0fdc7a43cd16'),
    'candidate': ('full-byte-pair-relations-generic-build-20261018-01',
                  '948c336c70b8e803b982cc88ea1f0cf3791c172c2c6f3fd090bb69bce1a98219'),
}
AFFINITY = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

def main():
    assert sorted(os.sched_getaffinity(0)) == AFFINITY
    receipts = {}
    identities = {}
    inputs = {}
    commands = []
    for side, (directory, expected_image) in SIDES.items():
        build = ROOT / directory
        receipt_path = build / 'receipt.json'
        receipt = json.loads(receipt_path.read_text())
        receipts[side] = receipt
        image = build / 'rook2-exact'
        assert sha(image) == expected_image == receipt['binary_output']['sha256']
        assert receipt['cargo_exit_code'] == 0
        assert receipt['source_sha256_before'] == receipt['source_sha256_after']
        assert receipt['tool_sha256_before'] == receipt['tool_sha256_after']
        assert receipt['source_identity_unchanged'] and receipt['tool_identity_unchanged']
        source_map = receipt['source_sha256_before'] | receipt['tool_sha256_before']
        assert len(receipt['source_sha256_before']) == 46
        assert len(receipt['tool_sha256_before']) == 23
        for relative, expected in source_map.items():
            path = build / 'source-before' / relative
            assert sha(path) == expected, str(path)
            inputs[str(path)] = expected
        for path in [image, receipt_path, build / 'build.stderr', build / 'archive-receipt.json', build / 'verified-source-before.tar.gz']:
            inputs[str(path)] = sha(path)
        destination = HERE / side
        destination.mkdir()
        for name, argv in [
            ('nm-demangled', ['/usr/bin/nm', '-n', '-S', '-C', str(image)]),
            ('nm-mangled', ['/usr/bin/nm', '-n', '-S', str(image)]),
            ('sections', ['/usr/bin/readelf', '-W', '-S', str(image)]),
            ('relocations', ['/usr/bin/readelf', '-W', '-r', str(image)]),
        ]:
            command = ['/usr/bin/taskset', '-c', '0-5,8-13', *argv]
            with (destination / (name + '.stdout')).open('xb') as out, \
                 (destination / (name + '.stderr')).open('xb') as err:
                returned = subprocess.run(command, stdout=out, stderr=err)
            commands.append(dict(side=side, name=name, argv=command,
                exit_code=returned.returncode, actual_child_return_observed=True))
            assert returned.returncode == 0
        identities[side] = dict(image=str(image), image_sha256=expected_image,
            receipt=str(receipt_path), receipt_sha256=sha(receipt_path),
            native_source_count=len(receipt['source_sha256_before']),
            rust_source_count=sum(path.endswith('.rs') for path in receipt['source_sha256_before']),
            tool_source_count=len(receipt['tool_sha256_before']))
    before, after = receipts['control'], receipts['candidate']
    for field in ['mode', 'target_triple', 'target_cpu', 'jobs', 'rust_flags',
                  'environment_overrides', 'build_effective_environment', 'toolchain',
                  'pgo', 'cargo_config_sha256_before', 'cargo_config_sha256_after']:
        assert before[field] == after[field], field
    assert before['tool_sha256_before'] == after['tool_sha256_before']
    assert before['source_sha256_before'].keys() == after['source_sha256_before'].keys()
    changes = [name for name, digest in before['source_sha256_before'].items()
               if digest != after['source_sha256_before'][name]]
    assert changes == ['src/influence.rs', 'src/relation_table.rs'], changes
    assert all(sha(path) == digest for path, digest in inputs.items())
    write(HERE / 'identity.json', dict(complete=True, images=identities,
        changed_native_sources=changes, exact_settings_match=True,
        source_input_sha256=inputs, commands=commands,
        native_engine_runs=0, build_runs=0, performance_claim=False))
    print(json.dumps(dict(complete=True, changes=changes, commands=len(commands), engine_runs=0)))

if __name__ == '__main__':
    main()
