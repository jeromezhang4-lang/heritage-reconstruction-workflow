from pathlib import Path
import base64
import html
import json
from .io import inside, dump

def build_gallery(root,case,out,models):
    assets={}
    wanted={s['share'] for s in case['scenes']}
    wanted.update(f[k] for f in case.get('failures',[]) for k in ['before','after'] if f.get(k))
    for rel in sorted(wanted):
        path=inside(root,rel)
        mime='image/png' if path.suffix.lower()=='.png' else 'image/jpeg'
        assets[rel]='data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode('ascii')
    data={'case':case,'assets':assets,'models':models,'obj':{k:(out/'model'/(k+'.obj')).read_text(encoding='utf-8') for k in models}}
    payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<',chr(92)+'u003c')
    web=Path(__file__).parent/'web'
    template=(web/'gallery.html').read_text(encoding='utf-8')
    template=template.replace('@@TITLE@@',html.escape(case['title'])).replace('@@STYLE@@',(web/'style.css').read_text(encoding='utf-8')).replace('@@DATA@@',payload).replace('@@SCRIPT@@',(web/'gallery.js').read_text(encoding='utf-8'))
    (out/'gallery.html').write_text(template,encoding='utf-8')
    dump(out/'GALLERY_SCOPE.json',{'standalone':True,'network_required':False,'external_source_links_require_network':True,'images':'recorded sharing assets; repaired/failed originals for comparisons','geometry':'regenerated core/context models; depth-tested WebGL viewer','historical_accuracy':'UNVERIFIED','recorded_images':len(case['scenes']),'ai_images_regenerated':False,'native_4k':[s.get('native_4k',False) for s in case['scenes']]})
