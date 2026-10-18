#!/usr/bin/env python3
"""Only execute after explicit parent clearance; verify reuse before new builds."""
import json,sys
from pathlib import Path
from guard import HERE,load,sha,require_clearance,terminal

def main():
 require_clearance();plan=load(HERE/'plan.json');reuse=load(HERE/'control-reuse.json');source=Path(plan['source_root'])
 sys.dont_write_bytecode=True;sys.path.insert(0,str(source/'tools'));from build import source_snapshot,tool_snapshot,cargo_configs
 assert source_snapshot(source)==plan['engine_source_sha256'] and tool_snapshot(source)==plan['tool_source_sha256']
 assert source_snapshot(Path(plan['control_source']))==plan['control_source_sha256'] and tool_snapshot(Path(plan['control_source']))==plan['tool_source_sha256']
 assert all(sha(Path(path))==h for path,h in reuse['metadata_sha256'].items())
 assert all(sha(Path(path))==h for path,h in plan['input_sha256'].items())
 assert sha(Path(reuse['artifact']))==reuse['artifact_sha256']=='e49219753e437e072bb7a3ddd53fc270419ee3a84464428f5b676b55ec51ab4f'
 assert sha(Path(reuse['profile']))==reuse['profile_sha256']=='2e6ba24a4b4e240fad3601de17569a128ce9b12f5019cabe7cae8d5a259a1170'
 root=HERE.parent
 use=load(root/'pgo-bounded-reply-baseline-use-build-20261018/receipt.json');inst=load(root/'pgo-bounded-reply-baseline-instrumented-build-20261018/receipt.json');generic=load(root/'ordered-bit-checkers-phase1-build-20261018/receipt.json');training=load(root/'pgo-bounded-reply-baseline-training-20261018/training.json');verification=load(root/'pgo-bounded-reply-baseline-training-20261018/verification.json');matched=load(root/'pgo-bounded-reply-matched-validation-20261018/independent-verification.json')
 assert matched['status']=='pass' and verification['complete'] and training['complete']
 assert use['source_sha256_before']==use['source_sha256_after']==inst['source_sha256_before']==training['engine_source_sha256']==plan['control_source_sha256']
 assert use['tool_sha256_before']==use['tool_sha256_after']==inst['tool_sha256_before']==generic['tool_sha256_before']==plan['tool_source_sha256']
 assert use['toolchain']==inst['toolchain']==generic['toolchain']
 assert cargo_configs(source)==cargo_configs(Path(plan['control_source']))==use['cargo_config_sha256_before']==inst['cargo_config_sha256_before']==generic['cargo_config_sha256_before']
 assert use['pgo']['input_sha256_before']==use['pgo']['input_sha256_after'] and use['pgo']['inputs_unchanged']
 assert training['profile_sha256']==verification['merged_profile_sha256']==reuse['profile_sha256']
 assert sha(root/'pgo-bounded-reply-baseline-training-20261018/training.json')==verification['training_record_sha256']
 for dirname,filename in [('pgo-bounded-reply-baseline-use-build-20261018','tool-terminal.json'),('pgo-bounded-reply-baseline-training-20261018','tool-terminal.json'),('pgo-bounded-reply-baseline-training-20261018','verify-tool-terminal.json'),('pgo-bounded-reply-baseline-use-check-20261018','tool-terminal.json'),('pgo-bounded-reply-matched-validation-20261018','tool-terminal.json')]:terminal(root/dirname/filename)
 for key in ['instrumented_build','raw','use_build','wire','reconciliation']:
  path=Path(plan[key]);assert not path.exists() and not path.is_symlink(),f'fresh absent path required: {path}'
 for target in ['dev-generic-pgo-generate','dev-generic-pgo-use']:assert not (source/'target'/target).exists(),'fresh candidate target required'
 output=dict(complete=True,control_same_artifact_reused=True,artifact_sha256=reuse['artifact_sha256'],control_profile_sha256=reuse['profile_sha256'],candidate_source_sha256=plan['engine_source_sha256'],tool_source_sha256=plan['tool_source_sha256'],input_sha256=plan['input_sha256'],control_reuse_record_sha256=sha(HERE/'control-reuse.json'),driver_sha256=sha(Path(__file__)),scope='No engines/builds; exact baseline artifact/profile reuse verified; candidate profile not yet exists')
 with (HERE/'readiness.json').open('x') as f:json.dump(output,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in output.items() if k not in ['candidate_source_sha256','tool_source_sha256','input_sha256']}))
if __name__=='__main__':main()
