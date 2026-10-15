from pathlib import Path
import urllib.request,json,hashlib
R=Path(__file__).resolve().parent
url='https://www.iranicaonline.org/uploads/files/Persepolis/persepolis_fig_2.jpg'
p=R.parents[1]/'outputs/Persepolis/01_Maps_Plans/Iranica_Figure2_Persepolis_Plan.jpg'
for attempt in range(2):
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'HistoricalResearch/1.0','Referer':'https://www.iranicaonline.org/articles/persepolis/'})
  with urllib.request.urlopen(req,timeout=40) as r:p.write_bytes(r.read())
  print(p,p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest());break
 except Exception as e:
  print(attempt,type(e).__name__,str(e)[:150])
  if attempt==1:raise
