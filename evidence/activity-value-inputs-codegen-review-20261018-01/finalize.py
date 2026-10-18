"""Bind closed bounded static-capture outputs without any new native command."""
from pathlib import Path
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    identity=json.loads((HERE/'identity.json').read_text())
    analysis=json.loads((HERE/'bounded-analysis.json').read_text())
    structural={}
    for name in ['king-pressure','q','ordinary','ordering','charge','evaluation','root-run']:
        left=(HERE/'control'/(name+'.signature.txt')).read_text().splitlines()
        right=(HERE/'candidate'/(name+'.signature.txt')).read_text().splitlines()
        assert len(left)==len(right)
        differences=[(a,b) for a,b in zip(left,right) if a!=b]
        # Report this restricted property separately, never as referent equality.
        only_referents=all('[PCREL ' in a and '[PCREL ' in b and
            re.sub(r'\[PCREL [^]]*\]','[PCREL]',a)==re.sub(r'\[PCREL [^]]*\]','[PCREL]',b)
            for a,b in differences)
        assert only_referents, name
        structural[name]=dict(differing_instruction_lines=len(differences),
            differences_limited_to_pc_relative_referents=True,
            referent_payload_not_generally_proved=True)
    assert all(sha(path)==digest for path,digest in identity['source_input_sha256'].items())
    files={str(path.relative_to(HERE)):dict(bytes=path.stat().st_size,sha256=sha(path))
        for path in sorted(HERE.rglob('*')) if path.is_file() and
        path.name not in ['output-manifest.json','review-summary.json','tool-terminal.json']}
    with (HERE/'output-manifest.json').open('x') as out:
        json.dump(files,out,indent=2);out.write('\n')
    summary=dict(complete=True,scope='static own generic images only',
        images=identity['images'],structural_observations=structural,
        exact_settings_match=True,changed_native_sources=['src/activity.rs'],
        raw_commands=24,native_engine_runs=0,build_runs=0,profiler_runs=0,
        recommendation='Bounded matched reported-only CPU trial justified after parent clearance; no predicted gain or adoption',
        performance_claim=False,all_owned_processes_terminal=True,
        observed_outer_terminals=[dict(session_id=None,chunk_id=chunk,exit_code=0,
            actual_tool_terminal_observed=True) for chunk in ['c218ca','6da103','659729','3c1b79']],
        final_helper_terminal_reported_separately=True,
        output_manifest_sha256=sha(HERE/'output-manifest.json'))
    with (HERE/'review-summary.json').open('x') as out:
        json.dump(summary,out,indent=2);out.write('\n')
    print(json.dumps(dict(complete=True,files=len(files),all_owned_processes_terminal=True,
        review_sha256=sha(HERE/'review.md'),summary_sha256=sha(HERE/'review-summary.json'),
        manifest_sha256=sha(HERE/'output-manifest.json'),structural=structural)))

if __name__=='__main__':main()
