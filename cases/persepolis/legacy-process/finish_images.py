from pathlib import Path
import sys,json,hashlib,signal,time,shutil
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;O=R.parents[1]/'outputs/Persepolis';OLD=Path('<BRONZE_PROJECT>/work')
sys.path.insert(0,str(OLD));from superresolve import upscale
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/'sr_models/FSRCNN_x3.pb')=='efd38655a815908c6c8954db6052f128e76a735f1de657894c477d0dc0b64481'
def timeout(s,f):raise TimeoutError('180-second image deadline')
signal.signal(signal.SIGALRM,timeout)
records=[];prompts=json.loads((O/'04_Images/PROMPT_MANIFEST.json').read_text());cams=json.loads((O/'02_Model/cameras.json').read_text())+[json.loads((O/'02_Model/context_camera.json').read_text())]
for i,(pr,cam) in enumerate(zip(prompts,cams),1):
 id=pr['id'];src=O/f'04_Images/Native/{id}.png';dest=O/f'04_Images/{id}_4K.png'
 if len(sys.argv)>1 and id not in sys.argv[1:]:continue
 cached=O/f'04_Images/{id}.metadata.json'
 if cached.exists() and dest.exists():
  old=json.loads(cached.read_text());jpg=O/old['sharing_derivative']['file']
  if old['native_sha256']==sha(src) and old['final_sha256']==sha(dest) and jpg.exists() and old['sharing_derivative']['sha256']==sha(jpg):
   records.append(old);print(id,'existing verified4K reused',flush=True);continue
 with Image.open(src) as im:im.load();native=list(im.size);fmt=im.format
 assert fmt=='PNG';signal.alarm(180)
 try:
  if native==[3840,2160]:shutil.copy2(src,dest);sr={'native_4k':True,'native_size':native,'final_size':native,'source_sha256':sha(src),'output_sha256':sha(dest)}
  else:sr=upscale(src,dest)
 finally:signal.alarm(0)
 with Image.open(dest) as im:
  assert im.size==(3840,2160);rgb=im.convert('RGB');rgb.save(O/f'04_Images/{id}_Share_4K.jpg',quality=89,optimize=True,subsampling=0)
 jpg=O/f'04_Images/{id}_Share_4K.jpg'
 rec={'id':id,'actual_tool':'built-in image_gen.imagegen','actual_generated':True,'native_file':str(src.relative_to(O)),'native_dimensions':native,'native_sha256':sha(src),'final_file':str(dest.relative_to(O)),'final_dimensions':[3840,2160],'final_sha256':sha(dest),'upscaling':sr,'sharing_derivative':{'file':str(jpg.relative_to(O)),'dimensions':[3840,2160],'lossy':True,'sha256':sha(jpg)},'camera':cam,'prompt':pr,'input_reference_sha256':sha(O/pr['references'][0]),'style_input_sha256':sha(O/pr['references'][1]),'geometry_version':'final-stair-revision' if i>1 else'initial main mesh with final stair-reference targeted edits','provider_model':'UNVERIFIED_NOT_EXPOSED','seed':'UNVERIFIED_NOT_EXPOSED','strict_pixel_mesh_fit':'UNVERIFIED','independent_archaeological_review':'NOT_PERFORMED'}
 rec['second_input_sha256']=rec.pop('style_input_sha256')
 names=[f'{id}.prompt.txt']
 if id=='PP01':
  names=['PP01_initial.prompt.txt','PP01_repair.prompt.txt','PP01_repair2.prompt.txt'];rec['input_reference_sha256']=sha(O/'06_Quality_Assurance/PP01_Input_Structure_v1.png');rec['initial_model_sha256']=sha(O/'06_Quality_Assurance/PP01_Input_Model_v1.obj');rec['final_edit_inputs']=[{'file':'04_Images/Native/PP01_repair1.png','sha256':sha(O/'04_Images/Native/PP01_repair1.png')},{'file':'03_References/Stair_Detail_Structure.png','sha256':sha(O/'03_References/Stair_Detail_Structure.png')}]
 if id in ['PP04','PP05']:names=[f'{id}.prompt.txt',f'{id}_repair.prompt.txt']
 if id=='PP02':names=['PP02_initial.prompt.txt','PP02.prompt.txt'];rec['rejected_initial_reason']='Wrong aerial direction repeated master camera'
 if id=='PP11':rec['geometry_version']='regional context layer reuses final core';rec['regional_obj_sha256']=sha(O/'02_Model/Persepolis_Regional_Context.obj');rec['region_occupancy_and_density']='HYPOTHETICAL_NOT_A_CENSUS';rec['distant_necropolis_detail']='Geographic context; facade count and exact430BCE appearance unverified'
 rec['actual_prompt_chain']=[{'path':'04_Images/Native/'+n,'sha256':sha(O/'04_Images/Native'/n)} for n in names]
 records.append(rec);(O/f'04_Images/{id}.metadata.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));print(id,native,'->3840x2160',round(sr.get('elapsed_seconds',0),2),'sec',flush=True)
(O/'04_Images/IMAGE_MANIFEST.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
sheet=Image.new('RGB',(1280,2160),'#f7efe1');d=ImageDraw.Draw(sheet)
for i,r in enumerate(records):
 with Image.open(O/r['final_file']) as im:
  im.thumbnail((640,360));x=i%2*640;y=i//2*360;sheet.paste(im,(x,y));d.text((x+12,y+12),r['id'],fill='white')
sheet.save(O/'06_Quality_Assurance/FINAL_CONTACT_SHEET.jpg',quality=92)
print(len(records),'actual 4K PNGs reopened; native and prompt/reference provenance preserved; full release requires11')
