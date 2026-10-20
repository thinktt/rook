#!/usr/bin/env python3
"""Future111 source composition. TEXT ONLY until explicit parent freeze clearance."""
from pathlib import Path
import difflib,hashlib,json
from guard import HERE,authorize,load,sha,write

def remove_once(text,fragment):
 assert text.count(fragment)==1,fragment
 return text.replace(fragment,'',1)
def read_owner(root,manifest):
 data={}
 for name,identity in manifest.items():
  rel=Path(name);assert not rel.is_absolute() and '..' not in rel.parts
  data[name]=(root/rel).read_bytes();assert hashlib.sha256(data[name]).hexdigest()==identity
 return data
def patch(before,after):
 out=[]
 for name in sorted(before.keys()|after.keys()):
  if before.get(name)==after.get(name):continue
  out.extend(difflib.unified_diff(before.get(name,b'').decode().splitlines(True),after.get(name,b'').decode().splitlines(True),fromfile='a/'+name if name in before else '/dev/null',tofile='b/'+name if name in after else '/dev/null'))
 return ''.join(out)
def main():
 authorize('freeze');plan=load(HERE/'composition-inputs.json')
 assert plan['status']=='PARENT_AUTHORIZED_EXACT_REVIEWED_INPUTS'
 roots={tag:Path(plan['parents'][tag]['path']) for tag in ['base109','generic110','joined110']}
 parents={tag:read_owner(root,plan['parents'][tag]['source_sha256']) for tag,root in roots.items()}
 base=parents['base109'];generic=parents['generic110'];joined=parents['joined110']
 assert (len(base),len(generic),len(joined))==(107,108,108)
 allowed_generic={'src/ordinary.rs','src/timed.rs','src/quiescence.rs','diagnostic/src/main.rs','diagnostic/src/actual_timed.rs','diagnostic/src/generic_timed.rs'}
 allowed_joined={'diagnostic/src/main.rs','diagnostic/src/joined_search.rs'}
 changed=lambda a,b:{n for n in a.keys()|b.keys() if a.get(n)!=b.get(n)}
 assert changed(base,generic)==allowed_generic and changed(base,joined)==allowed_joined
 assert all(sha(Path(name))==h for name,h in plan['authority_dependencies'].items())
 gm=generic['diagnostic/src/main.rs'].decode();jm=joined['diagnostic/src/main.rs'].decode();bm=base['diagnostic/src/main.rs'].decode()
 gmod='mod generic_timed;\n';garm='        "search.genericTimedSearch" => generic_timed::dispatch(input),\n'
 jmod='mod joined_search;\n';jarm='        "search.ordinaryJoinedSearch" => joined_search::dispatch(input),\n'
 strip_generic=lambda t:remove_once(remove_once(t,gmod),garm)
 strip_joined=lambda t:remove_once(remove_once(t,jmod),jarm)
 assert strip_generic(gm)==bm and strip_joined(jm)==bm
 assert gm.count('mod king_shelter;\n')==1 and gm.count('    match operation {\n')==1
 merged=gm.replace('mod king_shelter;\n','mod king_shelter;\n'+jmod,1).replace('    match operation {\n','    match operation {\n'+jarm,1)
 assert strip_joined(merged)==gm and strip_generic(merged)==jm and strip_joined(strip_generic(merged))==bm
 combined=dict(generic);combined['diagnostic/src/main.rs']=merged.encode();combined['diagnostic/src/joined_search.rs']=joined['diagnostic/src/joined_search.rs']
 assert len(combined)==109 and changed(generic,combined)==allowed_joined
 bucket=lambda name:'tools' if name.startswith('tools/') else 'cold' if name.startswith('diagnostic/') else 'native'
 grouped={key:{n:hashlib.sha256(v).hexdigest() for n,v in combined.items() if bucket(n)==key} for key in ['native','tools','cold']}
 assert tuple(len(grouped[k]) for k in ['native','tools','cold'])==(45,23,41)
 assert grouped['native']=={n:hashlib.sha256(v).hexdigest() for n,v in generic.items() if bucket(n)=='native'}
 assert grouped['tools']=={n:hashlib.sha256(v).hexdigest() for n,v in base.items() if bucket(n)=='tools'}
 target=Path(plan['destination']);out=Path(plan['evidence_output'])
 assert str(target).startswith('/home/legolas/rook2-work/') and not target.exists() and not target.is_symlink()
 assert not out.exists() and target not in roots.values()
 target.mkdir();out.mkdir()
 for name,data in combined.items():
  dest=target/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 manifest={n:hashlib.sha256(v).hexdigest() for n,v in combined.items()}
 write(out/'source-manifest.json',manifest)
 for key,values in grouped.items():write(out/(key+'-source-manifest.json'),values)
 for tag,data in parents.items():(out/('against-'+tag+'.patch')).write_text(patch(data,combined))
 write(out/'composition-proof.json',{'main_inverse_recovers_generic':True,'main_inverse_recovers_joined':True,'main_inverse_recovers109':True,'native_exact_generic':True,'tools_exact109':True,'joined_module_exact_latest_reviewed':True,'generic_projection_exact_reviewed':combined['diagnostic/src/actual_timed.rs']==generic['diagnostic/src/actual_timed.rs'],'source_files':109,'native':45,'tools':23,'cold':41,'source':str(target),'rust_parsed':False,'compiled_or_tested':False,'fixture_inventory_pending':True})
 # Recheck parents and authority after writing only the new destination.
 for tag,root in roots.items():assert read_owner(root,plan['parents'][tag]['source_sha256'])==parents[tag]
 assert all(sha(Path(name))==h for name,h in plan['authority_dependencies'].items())
 print(json.dumps({'status':'SOURCE_COMPOSED_NOT_EXECUTION_AUTHORIZED','source':str(target),'evidence':str(out)}))
if __name__=='__main__':main()
