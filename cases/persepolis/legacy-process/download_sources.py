from pathlib import Path
import urllib.request,time,json,hashlib
ROOT=Path(__file__).resolve().parent
items=[('OIP68.pdf','https://isac-assets.s3.amazonaws.com/isac-publications/oip68.pdf'),('Iranica_Persepolis.html','https://www.iranicaonline.org/articles/persepolis/'),('UNESCO_Persepolis.html','https://whc.unesco.org/en/list/114')]
records=[]
for name,url in items:
 p=ROOT/'sources'/name
 if p.exists() and p.stat().st_size>10000:
  records.append({'file':name,'url':url,'reused':True,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});continue
 for attempt in range(2):
  try:
   start=time.monotonic()
   req=urllib.request.Request(url,headers={'User-Agent':'HistoricalResearch/1.0'})
   with urllib.request.urlopen(req,timeout=45) as r,p.with_suffix('.partial').open('wb') as f:
    while True:
     chunk=r.read(1024*1024)
     if not chunk:break
     f.write(chunk)
     if time.monotonic()-start>240:raise TimeoutError('240 second download deadline')
   p.with_suffix('.partial').replace(p)
   records.append({'file':name,'url':url,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'status':'DOWNLOADED'})
   print(name,p.stat().st_size,'downloaded',flush=True);break
  except Exception as e:
   print(name,attempt,type(e).__name__,str(e)[:160],flush=True)
   if attempt==1:records.append({'file':name,'url':url,'status':'FAILED','error':type(e).__name__})
(ROOT/'DOWNLOAD_RECEIPT.json').write_text(json.dumps(records,indent=2))
