from html.parser import HTMLParser
from pathlib import Path
import re
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.out=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ['script','style']:self.skip+=1
  if t in ['p','div','h1','h2','h3','br']:self.out.append('\n')
 def handle_endtag(self,t):
  if t in ['script','style']:self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip:self.out.append(d)
R=Path(__file__).resolve().parent
for name in ['Iranica_Persepolis','UNESCO_Persepolis']:
 p=Parser();p.feed((R/'sources'/f'{name}.html').read_text());t=re.sub(r'\n\s*\n','\n',''.join(p.out));(R/'sources'/f'{name}.txt').write_text(t)
 if name.startswith('Iranica'):
  terms=['Tachara','Tačara','Hadīš','Palace D','Palace G','Residential']
  for line in t.splitlines():
   if any(k.casefold() in line.casefold() for k in terms):print(line[:2200])
