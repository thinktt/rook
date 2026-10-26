#!/usr/bin/env python3
"""One bounded saved-image lowering/layout observation; never runs an engine.

Imports and audit_result only read files. main runs objdump and readelf once per
image, retaining full output outside Git. Missing type/line information is an
explicit observation, not inferred layout or a reason to tune the candidate.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from common import CONTROL_SHA, image_layout, read, sha, snapshot, write

SCHEMA = 'rook2-completion-fence-lowering-v1'
TOOLS = {'objdump': Path('/usr/bin/objdump'), 'readelf': Path('/usr/bin/readelf')}
CONTROL_CRATE = Path('/home/legolas/rook2-experiments/workspaces/q-owner-local-20261026-01')
CANDIDATE_CRATE = Path('/home/legolas/rook2-experiments/workspaces/completion-fence-20261026-01')
WORKER = 'src/colors_worker.rs'
CAP_SECONDS = 120
RAW_CAP = 128 * 1024 * 1024


def declarations(path):
    """Literal top-level declarations in the sole changed source file.

    The concrete worker uses braced declarations ending at column zero and
    single-line attributes. Reject an unsupported shape instead of guessing.
    Test-only TestGate/TestHooks declarations are excluded by their cfg(test).
    Other source files are required byte-identical in declaration_proof.
    """
    text = path.read_bytes().decode('utf-8')
    lines = text.splitlines(keepends=True)
    found = {}
    for index, line in enumerate(lines):
        match = re.match(r'^(?:pub(?:\([^)]*\))?\s+)?(?:struct|enum)\s+(\w+)\b', line)
        if not match:
            continue
        start = index
        while start and lines[start-1].startswith('#['):
            start -= 1
        attributes = ''.join(lines[start:index])
        if '#[cfg(test)]' in attributes:
            continue
        assert '{' in line, ('unsupported worker declaration', line)
        end = index + 1
        while end < len(lines) and not re.fullmatch(r'}\s*\n?', lines[end]):
            end += 1
        assert end < len(lines), ('unterminated declaration', match[1])
        value = ''.join(lines[start:end+1]).encode()
        assert match[1] not in found
        found[match[1]] = value
    assert {'Shared', 'Cells', 'Reader', 'Packet', 'SideOutput', 'Control', 'Flight'} <= set(found)
    return found


def declaration_proof(control, candidate, sources):
    assert len(sources['control']) == len(sources['candidate']) == 68
    assert set(sources['control']) == set(sources['candidate'])
    others = [name for name in sources['control'] if name != WORKER]
    assert all(sources['control'][name] == sources['candidate'][name] for name in others)
    old, new = declarations(control/WORKER), declarations(candidate/WORKER)
    assert old == new, 'production worker layout declarations changed'
    return dict(byteIdentical=True,
        types={name: dict(sha256=hashlib.sha256(value).hexdigest(), bytes=len(value))
               for name, value in old.items()},
        unchangedOtherRustFiles=[name for name in others if name.endswith('.rs')],
        scope='All non-worker snapshot files are byte-identical; every top-level production struct/enum in colors_worker.rs is literal-byte-identical, including attributes. cfg(test) type declarations excluded; no compiled-layout inference.')


def input_paths(control, image, old, new, sources):
    paths = [Path(__file__).resolve(), Path(__file__).with_name('common.py').resolve(),
        control, image, *[tool.resolve() for tool in TOOLS.values()]]
    # Bind the actual reused pure reader implementations as well as this adapter.
    paths += [Path(function.__code__.co_filename).resolve()
              for function in [image_layout, read, sha, snapshot, write]]
    paths += [crate/name for crate, source in [(old, sources['control']),
        (new, sources['candidate'])] for name in source]
    return sorted(set(paths))


def run_tool(out, label, name, argv, deadline_ns):
    began = time.monotonic_ns()
    record = dict(tool=name, argv=[str(x) for x in argv], pid=None, exit=None,
        failure=None, cleanupSignals=[], startedMonotonicNs=began,
        deadlineMonotonicNs=deadline_ns)
    child = None
    try:
        with (out/(label+'.stdout')).open('xb') as stdout, (out/(label+'.stderr')).open('xb') as stderr:
            child = subprocess.Popen(record['argv'], stdout=stdout, stderr=stderr,
                env=dict(os.environ, LC_ALL='C'), start_new_session=True)
            record['pid'] = child.pid
            while child.poll() is None:
                assert time.monotonic_ns() < deadline_ns, 'lowering inspection deadline'
                assert (out/(label+'.stdout')).stat().st_size <= RAW_CAP
                assert (out/(label+'.stderr')).stat().st_size <= 1024*1024
                time.sleep(.05)
            record['exit'] = child.returncode
            assert child.returncode == 0, (label, child.returncode)
            assert (out/(label+'.stderr')).stat().st_size == 0
            assert (out/(label+'.stdout')).stat().st_size <= RAW_CAP
            assert time.monotonic_ns() < deadline_ns
    except BaseException as error:
        record['failure'] = repr(error)
        if child is not None and child.poll() is None:
            for signum in [signal.SIGTERM, signal.SIGKILL]:
                try:
                    os.killpg(child.pid, signum)
                    record['cleanupSignals'].append(int(signum))
                except ProcessLookupError:
                    pass
                try:
                    child.wait(timeout=5)
                    break
                except subprocess.TimeoutExpired:
                    if signum == signal.SIGKILL:
                        raise
        if child is not None:
            record['exit'] = child.returncode
        raise
    finally:
        record['endedMonotonicNs'] = time.monotonic_ns()
        record['elapsedNs'] = record['endedMonotonicNs']-began
        for suffix in ['stdout', 'stderr']:
            path = out/(label+'.'+suffix)
            if path.exists():
                record[suffix] = path.name
                record[suffix+'Sha256'] = sha(path)
                record[suffix+'Bytes'] = path.stat().st_size
        write(out/(label+'.json'), record)
    return record


def dwarf_types(path, names):
    """Read concrete type/member DIE attributes when the image emits them."""
    result = {name: [] for name in names}
    stack, current = {}, None

    def value(raw):
        return re.sub(r'^(?:\([^)]*\)\s*:?[ \t]*)+', '', raw).lstrip(': ').strip()

    def number(raw):
        cleaned = value(raw or '')
        return int(cleaned, 0) if re.fullmatch(r'(?:0x[0-9a-fA-F]+|0|[1-9][0-9]*)', cleaned) else None

    def commit(entry):
        depth, tag, attrs = entry['depth'], entry['tag'], entry['attrs']
        for old in [key for key in stack if key >= depth]:
            del stack[old]
        namespaces = [value(item['attrs'].get('name', '')) for item in stack.values()
                      if item['tag'] == 'DW_TAG_namespace']
        name = value(attrs.get('name', ''))
        short = name.rsplit('::', 1)[-1]
        if tag in ['DW_TAG_structure_type', 'DW_TAG_enumeration_type'] and short in result \
            and ('colors_worker' in namespaces or 'colors_worker::' in name):
            observed = dict(die=entry['offset'], namespace=namespaces, name=name,
                byteSize=number(attrs.get('byte_size')), alignment=number(attrs.get('alignment')),
                alignmentBasis='DW_AT_alignment only; absent means unknown', members=[])
            result[short].append(observed)
            entry['observed'] = observed
        elif tag == 'DW_TAG_member' and 'observed' in stack.get(depth-1, {}):
            raw = attrs.get('data_member_location')
            stack[depth-1]['observed']['members'].append(dict(name=name,
                byteOffset=number(raw), locationAttribute=raw))
        stack[depth] = entry

    with path.open(errors='replace') as stream:
        for line in stream:
            header = re.match(r'^\s*<(\d+)><([0-9a-fA-F]+)>: Abbrev Number: \d+(?: \((DW_TAG_\w+)\))?', line)
            if header:
                if current is not None:
                    commit(current)
                current = dict(depth=int(header[1]), offset=header[2], tag=header[3], attrs={})
            elif current is not None:
                attr = re.search(r'DW_AT_(\w+)\s*:\s*(.*)', line)
                if attr:
                    current['attrs'][attr[1]] = attr[2].strip()
    if current is not None:
        commit(current)
    return {name: dict(available=bool(rows), observations=rows,
        missingMeaning='Not emitted or not attributable to colors_worker; size/alignment/offsets remain unknown')
        for name, rows in result.items()}


def function_ranges(source):
    text = source.read_text()
    result = {}
    for name in ['signal_completion', 'wait_completion']:
        match = re.search(r'^fn '+name+r'\b[\s\S]*?^}', text, re.M)
        assert match, name
        result[name] = [text.count('\n', 0, match.start())+1,
                        text.count('\n', 0, match.end())+1]
    return result


def handshake(out, label, dump, source):
    ranges = function_ranges(source)
    blocks, current = [], None
    with dump.open(errors='replace') as stream:
        for line in stream:
            match = re.match(r'^([0-9a-fA-F]+) <(.+)>:\s*$', line)
            if match:
                if current is not None:
                    blocks.append(current)
                current = dict(address=match[1], symbol=match[2], lines=[line], sourceMatch=False)
            elif current is not None:
                current['lines'].append(line)
                location = re.search(r'colors_worker\.rs:(\d+)', line)
                if location and any(low <= int(location[1]) <= high for low, high in ranges.values()):
                    current['sourceMatch'] = True
    if current is not None:
        blocks.append(current)
    colors = [block for block in blocks if 'colors_worker' in block['symbol']]
    selected = [block for block in blocks if block['sourceMatch'] or
                ('colors_worker' in block['symbol'] and any(name in block['symbol'] for name in ranges))]
    coverage = 'named-symbol-or-source-correlated' if selected else 'colors-worker-fallback' if colors else 'unresolved'
    selected = selected or colors
    text = ''.join(''.join(block['lines']) for block in selected)
    artifact = out/(label+'.handshake.asm')
    artifact.write_text(text)
    return dict(sourceLineRanges=ranges, coverage=coverage,
        symbols=[dict(address=block['address'], name=block['symbol'], sourceCorrelated=block['sourceMatch'])
                 for block in selected],
        colorsWorkerSymbols=[block['symbol'] for block in colors],
        assemblyArtifact=artifact.name, assemblyArtifactSha256=sha(artifact),
        observedInstructionTextCounts={name: len(re.findall(pattern, text)) for name, pattern in
            [('lock', r'\block\b'), ('xchg', r'\bxchg\w*\b'), ('mfence', r'\bmfence\b')]},
        interpretation='Counts cover selected actual symbol blocks, including inlined neighboring work; they do not prove a fence-to-instruction mapping or cache cause. Redundant machine fences may legitimately coalesce. Full objdump output is retained.')


def audit_result(path, control, image, controlcrate, candidatecrate):
    """Read-only admission API; never invokes binutils, compiler or engine."""
    path = Path(path).resolve()
    record = read(path)
    assert record['schema'] == SCHEMA and record['complete'] is True
    assert record['control'] == image_layout(Path(control).resolve())
    assert record['control']['sha256'] == CONTROL_SHA
    assert record['candidate'] == image_layout(Path(image).resolve())
    old, new = Path(controlcrate).resolve(), Path(candidatecrate).resolve()
    assert record['controlCrate'] == str(old) and record['candidateCrate'] == str(new)
    sources = dict(control=snapshot(old), candidate=snapshot(new))
    assert record['sourceSha256'] == sources
    assert record['declarations'] == declaration_proof(old, new, sources)
    assert set(record['inputSha256']) == {str(item) for item in input_paths(
        Path(control).resolve(), Path(image).resolve(), old, new, sources)}
    for name, digest in record['inputSha256'].items():
        assert sha(name) == digest, name
    expected_raw = {label+'.'+tool+'.'+suffix for label in ['control', 'candidate']
        for tool in ['objdump', 'readelf'] for suffix in ['json', 'stdout', 'stderr']}
    expected_raw |= {label+'.handshake.asm' for label in ['control', 'candidate']}
    assert set(record['rawSha256']) == expected_raw
    for name, digest in record['rawSha256'].items():
        raw = path.parent/name
        assert raw.parent == path.parent and raw.is_file() and not raw.is_symlink()
        assert sha(raw) == digest, name
    assert record['elapsedNs'] == record['endedMonotonicNs']-record['startedMonotonicNs'] > 0
    assert record['endedMonotonicNs'] < record['deadlineMonotonicNs'] == record['startedMonotonicNs']+CAP_SECONDS*10**9
    expected = [(label, tool) for label in ['control', 'candidate'] for tool in ['objdump', 'readelf']]
    assert len(record['toolRuns']) == len(expected)
    for run, (label, name) in zip(record['toolRuns'], expected):
        target = Path(control).resolve() if label == 'control' else Path(image).resolve()
        options = ['-d', '-C', '-l'] if name == 'objdump' else ['--debug-dump=info']
        assert run['argv'] == [str(TOOLS[name]), *options, str(target)]
        assert run == read(path.parent/(label+'.'+name+'.json'))
        assert run['exit'] == 0 and run['failure'] is None and run['cleanupSignals'] == []
        assert record['startedMonotonicNs'] <= run['startedMonotonicNs'] < run['endedMonotonicNs'] < record['deadlineMonotonicNs']
        for suffix in ['stdout', 'stderr']:
            assert sha(path.parent/run[suffix]) == run[suffix+'Sha256']
    return record


def main():
    def interrupted(signum, _frame):
        raise InterruptedError('external signal '+str(signum))
    for signum in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(signum, interrupted)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', type=Path, required=True)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--control-crate', type=Path, default=CONTROL_CRATE)
    parser.add_argument('--candidate-crate', type=Path, default=CANDIDATE_CRATE)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir()
    start = time.monotonic_ns()
    deadline = start+CAP_SECONDS*10**9
    control, image = args.control.resolve(), args.engine.resolve()
    old, new = args.control_crate.resolve(), args.candidate_crate.resolve()
    record = dict(schema=SCHEMA, complete=False, startedMonotonicNs=start,
        deadlineMonotonicNs=deadline, toolRuns=[])
    try:
        sources = dict(control=snapshot(old), candidate=snapshot(new))
        inputs = input_paths(control, image, old, new, sources)
        assert sha(control) == CONTROL_SHA
        record.update(control=image_layout(control), candidate=image_layout(image),
            controlCrate=str(old), candidateCrate=str(new), sourceSha256=sources,
            declarations=declaration_proof(old, new, sources),
            inputSha256={str(path): sha(path) for path in sorted(set(inputs))}, observed={})
        for label, target, crate in [('control', control, old), ('candidate', image, new)]:
            for name, options in [('objdump', ['-d', '-C', '-l']), ('readelf', ['--debug-dump=info'])]:
                record['toolRuns'].append(run_tool(out, label+'.'+name, name,
                    [TOOLS[name], *options, target], deadline-10*10**9))
            record['observed'][label] = dict(
                types=dwarf_types(out/(label+'.readelf.stdout'), record['declarations']['types']),
                handshake=handshake(out, label, out/(label+'.objdump.stdout'), crate/WORKER))
        assert all(sha(path) == digest for path, digest in record['inputSha256'].items())
        record.update(complete=True, endedMonotonicNs=time.monotonic_ns(),
            notes='One existing control and one new generic image inspected once each; no execution, build, tuning or assertion that source-level fences require redundant machine instructions. DWARF omission is unknown layout, not equality evidence.')
        record['elapsedNs'] = record['endedMonotonicNs']-start
        assert record['endedMonotonicNs'] < deadline
        record['rawSha256'] = {path.name: sha(path) for path in sorted(out.iterdir()) if path.is_file()}
        write(out/'result.json', record)
        audit_result(out/'result.json', control, image, old, new)
        assert time.monotonic_ns() < deadline, 'lowering audit completion deadline'
    except BaseException as error:
        record.update(complete=False, failure=repr(error), endedMonotonicNs=time.monotonic_ns())
        record['elapsedNs'] = record['endedMonotonicNs']-start
        write(out/'failure.json', record)
        raise
    print(json.dumps(dict(complete=True, result=str(out/'result.json'),
        controlSha256=record['control']['sha256'], candidateSha256=record['candidate']['sha256'])))


if __name__ == '__main__':
    main()
