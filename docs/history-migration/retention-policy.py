from pathlib import PurePosixPath
import re
CODE={'.rs','.py','.mjs','.js','.c','.h','.sh','.bash','.cpp','.hpp','.toml','.lock','.patch','.diff'}
REPORT={'.md','.csv'}
TOKENS=re.compile(r'(^|[-_.])(plan|schema|proposal|contract|receipt|proof|decision|selection|summary|manifest|pins|provenance|closure|verification|prepared|activation|acceptance|verdict|frozen-image|result|report|config|method|command|workload|workloads|limits|protocol)([-_.]|$)')
BUILD={'.git','target','__pycache__','.fingerprint','incremental','deps','build'}
RAW={'cases','runs','requests','samples','replays','lifetimes','measured','warmups'}
def classify(path, size=None):
 p=PurePosixPath(path);parts=p.parts
 if not parts or parts[0]!='evidence':return 'project'
 if any(x in BUILD for x in parts[1:-1]):return None
 suffix=PurePosixPath(p.name.split('.before-')[0]).suffix
 if suffix in CODE and (size is None or size<=2097152):return 'setup-source'
 if suffix in REPORT and (size is None or size<=131072):return 'concise-report'
 if suffix=='.json' and TOKENS.search(p.name) and not any(x in RAW or re.fullmatch(r'(profile-\d+|case[-_]?\d+|run[-_]?\d+)',x) for x in parts[1:-1]) and (size is None or size<=131072):return 'setup-metadata'
 if (p.name=='cursor' or (p.suffix=='.bin' and any(t in str(p) for t in ['source-preparation','canary','malformed','fixture']))) and (size is None or size<=131072):return 'setup-input'
 return None
