"""Closed own-PGO evidence only. No source mutation or executable engine calls."""
from pathlib import Path
import gzip,hashlib,io,json,tarfile,sys
HERE=Path(__file__).resolve().parent
EVIDENCE=HERE.parent
NAMES=['complete117-pgo-preparation-20261018','complete117-pgo-instrumented-build-20261018','complete117-pgo-training-20261018','complete117-pgo-use-build-20261018','complete117-pgo-use-check-20261018','complete117-pgo-interruption-wire-20261018','complete117-pgo-reconciliation-20261018','complete117-pgo-review-fixes-proposal-20261018']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def write(name,value):
 with (HERE/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def selected():
 out=[]
 for name in NAMES:
  root=EVIDENCE/name
  assert root.is_dir() and not root.is_symlink()
  for p in sorted(root.rglob('*')):
   assert not p.is_symlink(),p
   if '__pycache__' in p.parts or 'target' in p.parts or p.suffix in ('.pyc','.pyo'):continue
   if p.is_file():out.append(p)
 plan=load(EVIDENCE/NAMES[0]/'plan.json')
 for path,digest in plan['input_sha256'].items():
  p=Path(path);assert p.is_file() and not p.is_symlink() and sha(p)==digest
  out.append(p)
 assert len(out)==len(set(out))
 return sorted(out)
def main():
 result=dict(complete=False,failure=None,scope='Closed exact117 own-PGO evidence, two-helper fix history, five pinned public replay/wire inputs only. No active pre-gate/CPU-prep or opaque files; no target/bytecode.',engine_runs=0,builds=0,training=0,profile_merges=0,timing=0)
 try:
  files=selected();before={str(p):dict(sha256=sha(p),bytes=p.stat().st_size,archive_member=str(p).lstrip('/')) for p in files}
  assert all('/target/' not in n and '__pycache__' not in n for n in before)
  assert len(list((EVIDENCE/'complete117-pgo-training-20261018/raw').glob('*.profraw')))==54
  images={str(EVIDENCE/'complete117-pgo-instrumented-build-20261018/rook2-exact'):'446d0de2aa66925d4f22ec217de8b5358e5156fad7b6e40c9482171ca71031e0',str(EVIDENCE/'complete117-pgo-use-build-20261018/rook2-exact'):'6a5ce6e27b74490e623fbb705f70c770ec12ff7e88f761fb0c7119ca2aee4a50'}
  assert all(before[path]['sha256']==digest for path,digest in images.items())
  manifest=dict(schema='rook2-own-pgo-original-path-manifest-v1',original_files=before,original_file_count=len(files),original_total_bytes=sum(v['bytes'] for v in before.values()),archive_member_convention='Original absolute path with leading slash removed; archive also contains checkpoint/original-path-manifest.json',selected_evidence_directories=NAMES,source_snapshots='Both tools/build.py source-before directories plus verified-source-before.tar.gz; no working target tree',excluded='All target and bytecode trees, active pre-gate/CPU-preparation outputs, unrelated/opaque files',exact_own_engine_images=images)
  write('original-path-manifest.json',manifest);manifest_bytes=(HERE/'original-path-manifest.json').read_bytes()
  archive=HERE/'complete117-own-pgo-evidence.tar.gz'
  with archive.open('xb') as output:
   with gzip.GzipFile(filename='',mode='wb',fileobj=output,mtime=0) as gz:
    with tarfile.open(fileobj=gz,mode='w|',format=tarfile.PAX_FORMAT) as tar:
     for p in files:
      data=p.read_bytes();entry=before[str(p)]
      assert len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256'],p
      info=tar.gettarinfo(str(p),arcname=entry['archive_member']);assert info.isfile();info.uid=1000;info.gid=1000;info.uname='legolas';info.gname='legolas'
      tar.addfile(info,io.BytesIO(data))
     info=tarfile.TarInfo('checkpoint/original-path-manifest.json');info.size=len(manifest_bytes);info.mode=0o644;info.mtime=0
     tar.addfile(info,io.BytesIO(manifest_bytes))
  expected={v['archive_member']:dict(sha256=v['sha256'],bytes=v['bytes']) for v in before.values()}
  expected['checkpoint/original-path-manifest.json']=dict(sha256=hashlib.sha256(manifest_bytes).hexdigest(),bytes=len(manifest_bytes))
  verified={}
  with tarfile.open(archive,'r:gz') as tar:
   for member in tar:
    assert member.isfile() and member.name in expected and member.name not in verified,member.name
    assert not member.name.startswith('/') and '..' not in Path(member.name).parts
    data=tar.extractfile(member).read();entry=expected[member.name]
    assert len(data)==member.size==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256'],member.name
    verified[member.name]=entry
  assert verified==expected
  assert selected()==files,'closed original file set changed'
  after={str(p):dict(sha256=sha(p),bytes=p.stat().st_size,archive_member=str(p).lstrip('/')) for p in files}
  assert before==after,'original content or size changed'
  result.update(complete=True,archive=str(archive),archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,manifest_sha256=sha(HERE/'original-path-manifest.json'),original_files=len(files),archive_members_verified=len(verified),all_originals_unchanged=True,all_members_independently_read_and_hashed=True,raw_profiles=54,exact_engine_images=images,all_own_pgo_native_stages_previously_terminal=True,outer_actual_tool_terminal_required=True)
 except BaseException as error:
  result['failure']=f'{type(error).__name__}: {error}'
 finally:write('archive-receipt.json',result)
 print(json.dumps(result));return 0 if result['complete'] else 1
if __name__=='__main__':sys.exit(main())
