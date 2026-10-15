from pathlib import Path
import urllib.request,time,hashlib,json,os
R=Path(__file__).resolve().parent;url='https://isac-idb-static.uchicago.edu/multimedia/1082/oic21.pdf';p=R/'sources/OIC21.pdf'
(R/'primary_download_pid.json').write_text(json.dumps({'pid':os.getpid(),'script':str(Path(__file__).resolve()),'url':url}))
for attempt in range(2):
 try:
  start=time.monotonic()
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HistoricalResearch/1.0'}),timeout=30) as r,p.with_suffix('.partial').open('wb') as f:
   while True:
    b=r.read(1024*1024)
    if not b:break
    f.write(b)
    if time.monotonic()-start>240:raise TimeoutError('240s deadline')
  p.with_suffix('.partial').replace(p);print('OIC21 downloaded',p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest(),flush=True);break
 except Exception as e:
  print(attempt,type(e).__name__,str(e)[:120],flush=True)
  if attempt==1:raise
