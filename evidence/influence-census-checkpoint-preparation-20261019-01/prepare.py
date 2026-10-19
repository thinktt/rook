#!/usr/bin/env python3
"""Finite metadata inventory only: never invokes Git or creates an archive."""
import hashlib
import json
import os
import stat
from pathlib import Path

ROOT = Path('/home/legolas/rook2')
HERE = Path(__file__).resolve().parent
TREES = (
    'influence-eligibility-census-source-preparation-20261019-01',
    'influence-eligibility-census-generic-build-20261019-01',
    'influence-eligibility-census-parent-review-20261019-01',
    'influence-eligibility-census-independent-source-review-20261019-01',
    'influence-eligibility-census-run-preparation-20261019-01',
    'influence-eligibility-census-analysis-20261019-01',
    'incremental-influence-feasibility-20261019-01',
    'incremental-influence-critical-review-20261019-01',
    'incremental-influence-advisor-review-20261019-01',
    'move-capacity-domain-audit-20261019-01',
    'ordering49-pgo-park-parent-commit-20261019-01',
    'influence-mask-cancel-delta-parent-selection-20261019-01',
)
BUILD = 'evidence/influence-eligibility-census-generic-build-20261019-01/'
EXCLUDED_FILE = BUILD+'rook2-exact'
EXCLUDED_PREFIX = BUILD+'source-before/'
PROMOTION = ROOT/'evidence/influence-bitsliced-sum-integration-20261019-01/source-promotion.json'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def digest(path):
    return sha(path.read_bytes())

def write_json(name, value):
    with (HERE/name).open('x') as f:
        json.dump(value,f,indent=2,sort_keys=True)
        f.write('\n')

def write_text(name, value):
    with (HERE/name).open('x') as f:
        f.write(value)

def source_check():
    promotion=json.loads(PROMOTION.read_text())
    assert promotion['experiment']==43 and promotion['promoted']
    assert promotion['combined_source115_graph']=='8a49fa28a0f79855ed798c97b87a28cda8895e786df9ca1e836065799be7db3a'
    expected=promotion['files_sha256']
    assert len(expected)==115
    actual={name:digest(ROOT/name) for name in expected}
    assert actual==expected, 'Canonical source differs from accepted43'
    return {'promotion_path':str(PROMOTION),'promotion_sha256':digest(PROMOTION),
            'source115_graph':promotion['combined_source115_graph'],
            'native72_graph':promotion['native_source72_graph'],
            'files_sha256':actual}

def inventory():
    selected={}; excluded={}; totals={}; whitespace={}
    for tree in TREES:
        base=ROOT/'evidence'/tree
        assert base.is_dir() and not base.is_symlink(), tree
        tc=tb=ec=eb=0
        for directory, dirs, files in os.walk(base,followlinks=False):
            dirs.sort();files.sort()
            for name in dirs:
                p=Path(directory)/name
                assert stat.S_ISDIR(p.lstat().st_mode) and not p.is_symlink(), str(p)
            for name in files:
                p=Path(directory)/name
                st=p.lstat();assert stat.S_ISREG(st.st_mode) and not p.is_symlink(), str(p)
                relative=p.relative_to(ROOT).as_posix()
                assert all(part not in ('','..','.') for part in Path(relative).parts)
                assert not any(c in relative for c in '\n\r\0') and not relative.startswith('/')
                assert relative not in selected and relative not in excluded
                mode=stat.S_IMODE(st.st_mode)
                if relative==EXCLUDED_FILE or relative.startswith(EXCLUDED_PREFIX):
                    excluded[relative]={'bytes':st.st_size,'mode':format(mode,'04o'),
                        'reason':'Existing .gitignore ELF rule; no ELF bytes read' if relative==EXCLUDED_FILE else 'Existing .gitignore source-before rule; reproduced by selected verified source archive; no source-before bytes read'}
                    ec+=1;eb+=st.st_size
                    continue
                assert name not in ('rook2-exact','rook2-dev-exact','rook2-diag-exact')
                assert '__pycache__' not in p.parts and 'target' not in p.parts
                data=p.read_bytes()
                assert data[:4]!=b'\x7fELF',relative
                selected[relative]={'sha256':sha(data),'bytes':len(data),'mode':format(mode,'04o')}
                tc+=1;tb+=len(data)
                # Read-only approximation of default diff --check diagnostics.
                # Exact exclusions are check-only, never add/commit exclusions.
                if b'\0' not in data and not name.endswith(('.gz','.tar','.zip')):
                    lines=data.splitlines()
                    hits=[]
                    for line_no,line in enumerate(lines,1):
                        if line.endswith((b' ',b'\t')):
                            hits.append({'line':line_no,'kind':'blank-at-eol'})
                        indent=line[:len(line)-len(line.lstrip(b' \t'))]
                        if b' \t' in indent:
                            hits.append({'line':line_no,'kind':'space-before-tab'})
                    if lines and lines[-1].strip(b' \t')==b'':
                        hits.append({'line':len(lines),'kind':'blank-at-eof'})
                    if hits or name.endswith('.patch'):
                        whitespace[relative]={'sha256':selected[relative]['sha256'],
                            'reason':'Exact stored diff/patch bytes including context; preserve without normalization' if name.endswith('.patch') else 'Exact retained evidence bytes; preserve original whitespace',
                            'default_whitespace_observations':hits}
        totals['evidence/'+tree]={'selected_files':tc,'selected_bytes':tb,'excluded_files':ec,'excluded_bytes':eb}
    assert len(TREES)==12 and len(selected)==len(set(selected))
    assert EXCLUDED_FILE in excluded
    assert any(n.startswith(EXCLUDED_PREFIX) for n in excluded)
    assert BUILD+'verified-source-before.tar.gz' in selected
    assert 'evidence/influence-eligibility-census-parent-review-20261019-01/analysis-review.json' in selected
    for case in ('profile-35','profile-08'):
        for name in ('census.json','stdout.raw','stderr.raw','native.json','command.json','checker.stdout','checker.stderr'):
            assert f'evidence/influence-eligibility-census-run-preparation-20261019-01/run/{case}/{name}' in selected
    return selected,excluded,totals,whitespace

def main():
    before_source=source_check()
    selected,excluded,totals,whitespace=inventory()
    # Check closed inputs and canonical source a second time before publishing.
    assert inventory()==(selected,excluded,totals,whitespace)
    assert source_check()==before_source
    write_json('manifest.json',{'schema':'finite-git-checkpoint-original-file-manifest-v1',
        'repository':str(ROOT),'trees':['evidence/'+n for n in TREES],
        'files':selected,'totals_by_tree':totals,'selected_files':len(selected),
        'selected_bytes':sum(v['bytes'] for v in selected.values())})
    write_json('exclusions.json',{'files':excluded,'excluded_files':len(excluded),
        'excluded_bytes':sum(v['bytes'] for v in excluded.values()),
        'scope':'Only exact existing ignored ELF and source-before payloads inside the12 finite trees; no deletion or normalization',
        'outside_scope':'Open50 implementation/preparation/build trees and every other evidence/root/untracked path; not inventoried or selected'})
    write_json('whitespace-check-exclusions.json',{'check_only':True,'never_exclude_from_commit':True,
        'files':whitespace,'scope':'Exact literal paths, preserving stored patch/raw bytes; parent must perform actual Git diff --check with these paths excluded only from that check',
        'git_whitespace_check_executed':False})
    write_text('selected-paths.txt',''.join(n+'\n' for n in sorted(selected)))
    write_text('whitespace-check-exclusions.txt',''.join(':(exclude,literal)'+n+'\n' for n in sorted(whitespace)))
    write_json('canonical-source-proof.json',{'complete':True,'canonical43_source115_unchanged':True,
        'before_equals_after':True,**before_source,'source_files_selected_for_commit':False})
    write_text('proposed-commit-message.txt',
        'Record closed influence eligibility census and delta selection\n\n'
        'Preserve the two-case count-only census, independent reconciliation, source/build provenance, and bounded feasibility, advisor, capacity, and parent decision records. Retain production43; the separate50 selection is source-only and counts imply no CPU gain.\n\n'
        'Co-authored-by: Codex GPT-6.1 Sol <codex@openai.com>\n'
        'Co-authored-by: Codex GPT-6 Astra <codex@openai.com>\n'
        'Directed-by: Tobias Toland <github@thinktt.e4ward.com>\n')
    write_json('preflight.json',{'complete':True,'trees':12,'selected_files':len(selected),
        'selected_bytes':sum(v['bytes'] for v in selected.values()),'excluded_files':len(excluded),
        'exact_whitespace_check_exclusions':len(whitespace),'selected_inventory_stable':True,
        'canonical115_unchanged':True,'symlink_or_nonregular_entries':0,'unsafe_or_duplicate_paths':0,
        'elf_bytes_read':0,'git_commands':0,'archive_commands':0,'native_commands':0,
        'source_or_prior_evidence_mutations':0,'parent_review_and_commit_required':True})
    print(json.dumps({'complete':True,'trees':12,'selected_files':len(selected),
        'selected_bytes':sum(v['bytes'] for v in selected.values()),'excluded_files':len(excluded),
        'whitespace_check_exclusions':len(whitespace),'manifest_sha256':digest(HERE/'manifest.json'),
        'canonical115_unchanged':True,'git_commands':0}))

if __name__=='__main__':
    main()
