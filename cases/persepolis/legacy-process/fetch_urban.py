from pathlib import Path
import urllib.request,json,hashlib,time
R=Path(__file__).resolve().parent;O=R.parents[1]/'outputs/Persepolis';records=[]
items=[('Regional_Sectors_Source.jpg','https://archeologie.culture.gouv.fr/sites/archeologie/files/styles/archeologie_home_media/public/upload/master/visuel/GSA_Persepolis_Image4.jpg?itok=WG8fP8Vh'),('Royal_Precinct_Source.jpg','https://archeologie.culture.gouv.fr/sites/archeologie/files/styles/archeologie_home_media/public/upload/master/visuel/GSA_Persepolis_Image6.jpg?itok=n5RfK6WB'),('Urban_Research.html','https://archeologie.culture.gouv.fr/fr/persepolis'),('SELOPerse_report.html','https://cordis.europa.eu/project/id/299665/reporting/es')]
for name,url in items:
 p=O/'01_Maps_Plans'/name if name.endswith('.jpg') else R/'sources'/name
 for attempt in range(2):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'HistoricalResearch/1.0'})
   with urllib.request.urlopen(req,timeout=35) as r:p.write_bytes(r.read())
   records.append({'file':str(p),'url':url,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});print(name,p.stat().st_size,flush=True);break
  except Exception as e:
   print(name,attempt,type(e).__name__,str(e)[:120],flush=True)
   if attempt==1:records.append({'file':name,'url':url,'status':'FAILED'})
(R/'URBAN_DOWNLOAD_RECEIPT.json').write_text(json.dumps(records,indent=2))
