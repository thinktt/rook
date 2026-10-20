"""Seal closed bounded review output hashes without native execution."""
from pathlib import Path
import hashlib
import json
HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
identity=json.loads((HERE/'identity.json').read_text())
assert all(sha(path)==digest for path,digest in identity['source_input_sha256'].items())
manifest={str(path.relative_to(HERE)):dict(bytes=path.stat().st_size,sha256=sha(path))
    for path in sorted(HERE.rglob('*')) if path.is_file() and path.name not in ['output-manifest.json','tool-terminal.json']}
with (HERE/'output-manifest.json').open('x') as out:
    json.dump(manifest,out,indent=2);out.write('\n')
print(json.dumps(dict(complete=True,files=len(manifest),all_owned_processes_terminal=True,
    review_sha256=sha(HERE/'review.md'),summary_sha256=sha(HERE/'review-summary.json'),
    manifest_sha256=sha(HERE/'output-manifest.json'),native_engine_runs=0)))
