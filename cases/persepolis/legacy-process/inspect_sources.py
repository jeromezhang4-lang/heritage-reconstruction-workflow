from pathlib import Path
import json,re
from html.parser import HTMLParser
from pypdf import PdfReader
R=Path(__file__).resolve().parent
class P(HTMLParser):
 def __init__(self):super().__init__();self.out=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ['script','style']:self.skip+=1
  if t in ['p','div','h1','h2','h3','br']:self.out.append('\n')
 def handle_endtag(self,t):
  if t in ['script','style']:self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip:self.out.append(d)
for n in ['Iranica_Persepolis','UNESCO_Persepolis']:
 p=P();p.feed((R/'sources'/f'{n}.html').read_text());t=re.sub(r'\n\s*\n','\n',''.join(p.out));(R/'sources'/f'{n}.txt').write_text(t)
doc=PdfReader(R/'sources/OIP68.pdf');print('OIP68 pages',len(doc.pages));index=[]
out=R/'sources/OIP68_text';out.mkdir(exist_ok=True)
for i,p in enumerate(doc.pages):
 t=p.extract_text() or '';(out/f'page_{i+1:03}.txt').write_text(t)
 u=t.upper()
 if any(q in u for q in ['GENERAL PLAN OF','PLAN OF THE TERRACE','PLAN OF PERSEPOLIS','RECONSTRUCTED PLAN','APADANA. PLAN','HUNDRED-COLUMN HALL. PLAN']):index.append({'pdf_page':i+1,'text':t[:450]})
(R/'sources/PDF_INDEX.json').write_text(json.dumps(index,ensure_ascii=False,indent=2));print(json.dumps(index[:24],ensure_ascii=False))
