"""AST/pure model/preflight checks only. No executable engine/compiler/merge calls."""
import ast,copy,hashlib,json,os,re,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import guard as g

def must_reject(f):
 try:f()
 except (AssertionError,FileNotFoundError,KeyError,TypeError):return True
 raise AssertionError('invalid control unexpectedly admitted')

def main():
 before=g.source_snapshot(g.SOURCE);tools=g.tool_snapshot(g.ROOT)
 parsed=[]
 for p in sorted(g.HERE.glob('*.py')):ast.parse(p.read_text(),filename=str(p));parsed.append(p.name)
 g.check_inputs()
 assert len(before)==46 and len(g.PLAN['tool_source_sha256'])==23
 assert len(g.PLAN['case_order'])==len(set(g.PLAN['case_order']))==54
 assert not (g.HERE/'execution-clearance.json').exists()
 missing=must_reject(g.require_clearance)
 # Deliberately synthetic authority fixtures are not execution/build receipts.
 with tempfile.TemporaryDirectory(prefix='rook2-pgo-offline-',dir=g.PLAN['tempdir']) as d:
  terminal=Path(d)/'terminal-fixture.json'
  terminal.write_text(json.dumps(dict(actual_tool_terminal_observed=True,exit_code=0,session_id='OFFLINE-FIXTURE',terminal_chunk_id='OFFLINE-FIXTURE')))
  c=dict(authorized=True,all_conflicting_native_work_terminal=True,scope='placement-pure-cache-own-pgo-validation-no-cpu',plan_sha256=g.sha(g.HERE/'plan.json'),source_root=str(g.SOURCE),prepared_scripts_sha256=g.load(g.HERE/'script-pins.json'),functional_candidate_accepted=True,generic_pilot_advance_accepted=True,generic_candidate_sha256=g.PLAN['generic_candidate_sha256'],generic_pilot_evidence={str(g.HERE/'plan.json'):g.sha(g.HERE/'plan.json')},generic_pilot_actual_terminals={str(terminal):g.sha(terminal)},functional_evidence={str(g.HERE/'plan.json'):g.sha(g.HERE/'plan.json'),g.PLAN['functional_proof_path']:g.PLAN['functional_proof_sha256']},actual_terminals={str(terminal):g.sha(terminal)},training_cpu=14,sibling15_no_owned_task=True,quiet_window_and_interference_review='OFFLINE-FIXTURE ONLY')
  assert g.validate_authority(c)==c
  negatives=0
  for key,value in [('authorized',False),('all_conflicting_native_work_terminal',False),('scope','wrong'),('plan_sha256','0'*64),('source_root','/wrong'),('prepared_scripts_sha256',{}),('functional_candidate_accepted',False),('generic_pilot_advance_accepted',False),('generic_candidate_sha256','0'*64),('generic_pilot_evidence',{}),('generic_pilot_actual_terminals',{}),('functional_evidence',{}),('actual_terminals',{}),('training_cpu',0),('sibling15_no_owned_task',False),('quiet_window_and_interference_review','')]:
   bad=copy.deepcopy(c);bad[key]=value;must_reject(lambda:g.validate_authority(bad));negatives+=1
  terminal.write_text(json.dumps(dict(actual_tool_terminal_observed=True,exit_code=1,session_id='OFFLINE-FIXTURE',terminal_chunk_id='OFFLINE-FIXTURE')))
  c['actual_terminals'][str(terminal)]=g.sha(terminal);must_reject(lambda:g.validate_authority(c));negatives+=1
 spec=Path('/home/legolas/king-spec/conformance/profiling')
 js=(spec/'replay-check.mjs').read_text();benchmark=(spec/'benchmark.mjs').read_text()
 imports=re.findall(r"(?:from\s+|import\s*\()(['\"])([^'\"]+)\1",js+benchmark)
 relative={name for _,name in imports if not name.startswith('node:')}
 assert relative=={'./benchmark.mjs'},relative
 oracle=g.load(spec/'replay-oracle.json');work=g.load(spec/'workloads.json')
 assert [c['id'] for c in work['cases']]==g.PLAN['case_order']
 assert {c['id'] for c in oracle['cases']}==set(g.PLAN['case_order'])
 from raw_model import semantic
 for answer in oracle['cases']:
  for p in answer['posts']:
   assert semantic(f"{p['depth']} {p['score']} {p['workThousands']} {p['searchId']} {p['pv']}")==p
 fixture=g.load(Path('/home/legolas/king-spec/conformance/fixtures/interrupted-sessions-v1.json'))
 assert len(fixture['cases'])==8 and sum(len(c['expected']['results']) for c in fixture['cases'])==24
 assert g.source_snapshot(g.SOURCE)==before and g.tool_snapshot(g.ROOT)==tools
 result=dict(complete=True,offline_only=True,ast_files=parsed,missing_clearance_rejected=missing,authority_negative_controls=negatives,public_js_relative_import_closure=sorted(relative),source_files=46,tools=23,case_order=54,wire_fixtures=8,wire_searches=24,root_tools_unchanged=True,native_executions=0,builds=0,training=0,profile_merges=0)
 g.write(g.HERE/'offline-controls.json',result);print(json.dumps(result))
if __name__=='__main__':main()
