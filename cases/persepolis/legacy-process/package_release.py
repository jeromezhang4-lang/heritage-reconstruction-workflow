from pathlib import Path
import json,hashlib,zipfile,time,signal
from PIL import Image
R=Path(__file__).resolve().parent;OUT=R.parents[1]/'outputs';O=OUT/'Persepolis';H=OUT/'Persepolis_Single_File.html'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def timeout(s,f):raise TimeoutError('240second packaging and verification deadline')
signal.signal(signal.SIGALRM,timeout);signal.alarm(240)
qa=json.loads((O/'06_Quality_Assurance/SINGLE_FILE_QA.json').read_text());assert qa['status']=='PASS' and qa['html_sha256']==sha(H) and qa['owned_browser_closed']
m=json.loads((O/'04_Images/IMAGE_MANIFEST.json').read_text());assert len(m)==11
for x in m:
 for key,pathkey in [('native_sha256','native_file'),('final_sha256','final_file')]:assert sha(O/x[pathkey])==x[key]
 with Image.open(O/x['final_file']) as im:assert im.size==(3840,2160)
for fn in ['MODEL_FREEZE.json','URBAN_ADDENDUM_FREEZE.json','SYNTHESIS_FREEZE.json']:
 for x in json.loads((O/'06_Quality_Assurance'/fn).read_text())['outputs']:assert sha(O/x['path'])==x['sha256'],x['path']
manifest_path=O/'06_Quality_Assurance/FINAL_FILE_MANIFEST.json'
files=sorted(p for p in O.rglob('*') if p.is_file() and p!=manifest_path and '__pycache__' not in p.parts)
filemanifest={'status':'FROZEN_AND_READBACK','files':[{'path':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files],'limitations':'Historical upper structures/colours and regional density remain conjectural. SHA proves artifact identity, not archaeological accuracy.'};manifest_path.write_text(json.dumps(filemanifest,ensure_ascii=False,indent=2));files.append(manifest_path)
ZIP=OUT/'Persepolis_Complete_Collection.zip';expected={}
with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:
  name='Persepolis/'+str(p.relative_to(O));expected[name]=sha(p);z.write(p,name)
 expected[H.name]=sha(H);z.write(H,H.name)
print('ZIP written',ZIP.stat().st_size,'bytes; verifying actual members',flush=True)
with zipfile.ZipFile(ZIP) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(set(z.namelist()))==len(expected)
 checks=[{'member':n,'sha256':hashlib.sha256(z.read(n)).hexdigest(),'expected_sha256':h} for n,h in expected.items()]
 assert all(c['sha256']==c['expected_sha256'] for c in checks)
assert all(sha(O/r['path'])==r['sha256'] for r in filemanifest['files'])
receipt={'status':'PASS','zip_path':ZIP.name,'zip_bytes':ZIP.stat().st_size,'zip_sha256':sha(ZIP),'members':len(checks),'crc':'PASS','per_member_sha256':'PASS','same_disk_artifacts_readback':'PASS','members_verified':checks}
(OUT/'Persepolis_ZIP_Verification.json').write_text(json.dumps(receipt,indent=2))
delivery={'status':'COMPLETE_WITH_DECLARED_HISTORICAL_LIMITATIONS','image_count':11,'source_count':9,'native_size':[1672,941],'final_size':[3840,2160],'native4K':False,'actual_model_objects':1883,'context_objects':2530,'offline_browser_qa':'PASS','owned_browser_closed':qa['owned_browser_closed'],'zip_crc_member_sha':'PASS','artifacts':[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in [H,ZIP,OUT/'Persepolis_ZIP_Verification.json']],'independent_archaeological_review':'NOT_PERFORMED','strict_AI_geometry_fit':'UNVERIFIED','regional_house_density':'HYPOTHETICAL'}
(OUT/'Persepolis_Delivery_Manifest.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2));(OUT/'Persepolis_CHECKSUMS.txt').write_text('\n'.join(f'{a["sha256"]}  {a["path"]}' for a in delivery['artifacts'])+'\n')
signal.alarm(0);print(json.dumps({k:v for k,v in delivery.items() if k!='artifacts'},ensure_ascii=False));print(json.dumps(delivery['artifacts'],ensure_ascii=False))
