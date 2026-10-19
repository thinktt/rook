#!/usr/bin/env python3
"""Preserve exactly the four closed own43 PGO screen trees; no ELF or live scope."""
from pathlib import Path, PurePosixPath
import gzip, hashlib, json, os, stat, tarfile
P = Path(__file__).resolve().parent
E = P.parent
H = {0,1,2,3,4,5,8,9,10,11,12,13}
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while block := f.read(1048576):
            h.update(block)
    return h.hexdigest()
def write(name, value):
    with (P/name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')
def inventory(roots):
    files, excluded = {}, []
    for name in roots:
        base = E/name
        assert base.is_dir() and not base.is_symlink(), base
        for q in sorted(base.rglob('*')):
            st = q.lstat()
            assert not stat.S_ISLNK(st.st_mode), q
            if stat.S_ISDIR(st.st_mode):
                continue
            assert stat.S_ISREG(st.st_mode), q
            path = str(q.relative_to(E)); posix = PurePosixPath(path)
            assert not posix.is_absolute() and '..' not in posix.parts
            assert '\\' not in path and '\x00' not in path and path not in files
            row = dict(sha256=sha(q), bytes=st.st_size, mode=stat.S_IMODE(st.st_mode))
            with q.open('rb') as f:
                elf = f.read(4) == b'\x7fELF'
            if elf:
                excluded.append(dict(path=path, **row, reason='Explicit parent exclusion: ELF image bytes retained at original path.'))
            else:
                files[path] = row
    return files, excluded

def main():
    assert os.sched_getaffinity(0) == H
    plan = json.loads((P/'plan.json').read_text())
    assert sha(P/'member-manifest.json') == plan['member_manifest_sha256']
    manifest = json.loads((P/'member-manifest.json').read_text())
    roots = plan['roots']
    assert roots == ['influence-bitsliced-sum-pgo-'+s+'-20261019-01' for s in ['backend-review','cpu-pilot-preparation','cpu-pilot','decision']]
    assert manifest['roots'] == roots
    files, excluded = inventory(roots)
    assert files == manifest['members'] and excluded == manifest['excluded_elf']
    archive = P/plan['archive']
    with archive.open('xb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0, compresslevel=9) as z:
            with tarfile.open(mode='w|', fileobj=z, format=tarfile.PAX_FORMAT) as tar:
                for name, row in sorted(files.items()):
                    source = E/name
                    assert sha(source) == row['sha256']
                    t = tarfile.TarInfo(name)
                    t.size = row['bytes']; t.mode = row['mode']
                    t.uid = t.gid = t.mtime = 0; t.uname = t.gname = ''
                    with source.open('rb') as f:
                        tar.addfile(t, f)
    with archive.open('rb') as f:
        header = f.read(10)
    assert header[:4] == b'\x1f\x8b\x08\x00' and header[4:8] == b'\x00'*4
    assert header[8] == 2  # gzip level9 marker; no filename or wall-clock metadata.
    seen = set(); reopened_bytes = 0
    with tarfile.open(archive, mode='r|gz') as tar:
        for member in tar:
            name = member.name
            assert member.isfile() and name in files and name not in seen
            assert name == sorted(files)[len(seen)]
            posix = PurePosixPath(name)
            assert not posix.is_absolute() and '..' not in posix.parts
            row = files[name]
            assert member.size == row['bytes'] and member.mode == row['mode']
            assert member.uid == member.gid == member.mtime == 0
            assert member.uname == member.gname == member.linkname == ''
            assert member.devmajor == member.devminor == 0
            assert set(member.pax_headers) <= {'path'}
            if member.pax_headers:
                assert member.pax_headers['path'] == name
            h = hashlib.sha256(); size = 0
            f = tar.extractfile(member); assert f is not None
            with f:
                while block := f.read(1048576):
                    h.update(block); size += len(block)
            assert size == row['bytes'] and h.hexdigest() == row['sha256']
            reopened_bytes += size; seen.add(name)
    assert seen == set(files) and reopened_bytes == manifest['unpacked_bytes']
    after, after_excluded = inventory(roots)
    assert after == files and after_excluded == excluded
    decision = json.loads((E/roots[-1]/'decision.json').read_text())
    receipt = dict(complete=True, archive=archive.name, archive_sha256=sha(archive), archive_bytes=archive.stat().st_size,
        members=len(files), unpacked_bytes=reopened_bytes, plan_sha256=sha(P/'plan.json'),
        member_manifest_sha256=sha(P/'member-manifest.json'), writer_sha256=sha(P/'archive_closed.py'),
        gzip_header=header.hex(), every_member_reopened=True, every_header_mode_size_hash_verified=True,
        sorted_safe_unique_complete_membership=True, originals_inventory_modes_and_hashes_unchanged=True,
        excluded_elf=excluded, candidate_own_pgo_sha256=decision['candidate_own_pgo_sha256'],
        control40_own_pgo_sha256=decision['control40_own_pgo_sha256'], original_raw70_preserved=True,
        scope='Four closed own43 PGO backend/pilot-preparation/raw70/decision trees only. No ELF, build/profile source archive, broad qualification, source promotion or live result inclusion.')
    write('archive-receipt.json', receipt)
    print(json.dumps(receipt))
if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        write('archive-failure.json', dict(complete=False, error=repr(error)))
        raise
