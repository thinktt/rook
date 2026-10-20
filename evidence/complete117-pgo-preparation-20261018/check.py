"""Future fresh post-use original54 and literal eight-wire24 regression."""
from guard import *

def main():
 require_clearance()
 build=Path(PLAN['use_build']);train=Path(PLAN['training']);out=Path(PLAN['use_check']);wire=Path(PLAN['wire'])
 for p in [build/'tool-terminal.json',train/'tool-terminal.json',train/'verify-tool-terminal.json']:terminal(p)
 assert not out.exists() and not wire.exists()
 b=load(build/'receipt.json');t=load(train/'training.json');v=load(train/'verification.json')
 assert b['pgo']['mode']=='profile-use' and b['pgo']['inputs_unchanged'] and t['complete'] and v['independent_remerge_byte_identical']
 assert b['source_sha256_before']==b['source_sha256_after']==t['engine_source_sha256']==PLAN['engine_source_sha256']
 assert b['pgo']['input_sha256_before']==b['pgo']['input_sha256_after']=={str(train/'merged.profdata'):sha(train/'merged.profdata'),str(train/'training.json'):sha(train/'training.json')}
 engine=build/'rook2-exact';identity=sha(engine);assert identity==b['binary_output']['sha256']
 out.mkdir()
 run(['/usr/bin/node','/home/legolas/king-spec/conformance/profiling/replay-check.mjs','--',str(engine)],out/'profile-all')
 r=load(out/'profile-all.stdout');assert r['status']=='pass' and r['selectedCases']==PLAN['case_order'] and len(r['results'])==54
 for row in r['results']:
  assert row['status']=='pass' and row['complete'] and not row['truncated'] and row['exit']==dict(code=0,signal=None) and row['stderr']=='' and row['error'] is None and row['discardedObservedBytes']==0 and not row.get('cleanupUnconfirmed',False)
 assert not (out/'profile-all.stderr').stat().st_size
 run([sys.executable,str(ROOT/'tools/check_live.py'),'--engine',str(engine),'--output',str(wire)],out/'wire')
 w=load(wire/'receipt.json');assert w['pass'] and len(w['results'])==8 and sum(len(x['searches']) for x in w['results'])==24
 assert all(x['complete_streams'] and x['observed_exit_code']==x['exit_code']==0 for x in w['results'])
 assert w['engine_sha256_before']==w['engine_sha256_after']==identity
 assert sha(engine)==identity;check_inputs()
 write(out/'identity.json',dict(complete=True,artifact_sha256=identity,profile_sha256=sha(train/'merged.profdata'),strict_replays=54,wire_fixtures=8,wire_searches=24,replay_sha256=sha(out/'profile-all.stdout'),wire_receipt_sha256=sha(wire/'receipt.json')))
if __name__=='__main__':main()
