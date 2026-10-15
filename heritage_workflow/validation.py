"""Explicit case validation; technical checks never certify historical truth."""
from pathlib import Path
import hashlib
import json
import math
import re
from .io import WorkflowError, inside, load, image_size, check_manifest, sha

def review_target(case,scene,root):
    """Bind a review to image bytes and the evidence/camera context, not just a scene name."""
    native=inside(root,scene['native'])
    data={'image_sha256':sha(native),'snapshot_bce':case.get('snapshot_bce'),'camera':scene['camera'],'claims':[x for x in case['claims'] if x['id'] in scene['claim_ids']],'components':[x for x in case['components'] if x['id'] in scene['component_ids']],'sources':case['sources']}
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def verify_case(root, hashes=True):
    root=Path(root).resolve(); c=load(root/'case.json'); errors=[]; warnings=[]
    required=['schema_version','id','title','sources','claims','components','scenes','geometry','limitations','release_kind']
    for k in required:
        if k not in c: errors.append('missing field: '+k)
    if errors: return {'status':'FAIL','errors':errors,'warnings':warnings}
    if c['schema_version']!='1.0': errors.append('unsupported schema_version')
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}',c['id']): errors.append('invalid case id')
    if c['release_kind'] not in ['documented_case_study','reconstruction_draft']: errors.append('invalid release_kind')
    if not isinstance(c['limitations'],list) or not c['limitations']: errors.append('limitations must be explicit')
    indexes={}
    for field in ['sources','claims','components','scenes']:
        values=c[field]
        if not isinstance(values,list) or not values: errors.append(field+' must be a nonempty list');continue
        ids=[v.get('id') for v in values]
        if any(not isinstance(v,str) or not v for v in ids): errors.append(field+': invalid id')
        if len(set(ids))!=len(ids): errors.append(field+': duplicate id')
        indexes[field]=set(ids)
    def refs(obj,key,target):
        values=obj.get(key,[])
        if not values: errors.append(obj.get('id','?')+': empty '+key)
        for v in values:
            if v not in indexes.get(target,set()): errors.append(obj.get('id','?')+': unknown '+key+' '+str(v))
    for s in c['sources']:
        if s.get('placeholder') or s.get('access')=='NOT_YET_READ': errors.append(s['id']+': research placeholder has not been replaced')
        if not s.get('url','').startswith(('https://','http://')): errors.append(s['id']+': source URL required')
        if not s.get('access'): errors.append(s['id']+': actual source access/scope must be recorded')
    for claim in c['claims']:
        refs(claim,'source_ids','sources')
        if not claim.get('text') or not claim.get('limitation'): errors.append(claim['id']+': text and limitation required')
        if not claim.get('certainty') or any(t not in ['A','B','C','D','UNKNOWN'] for t in claim['certainty']): errors.append(claim['id']+': invalid certainty')
    for comp in c['components']:
        refs(comp,'claim_ids','claims')
        dims=comp.get('dimensions_m',[])
        if len(dims)!=3 or any(not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0 for v in dims): errors.append(comp['id']+': dimensions must be three positive finite numbers')
    for scene in c['scenes']:
        refs(scene,'claim_ids','claims');refs(scene,'component_ids','components')
        cam=scene.get('camera',{})
        if cam.get('id')!=scene['id']: errors.append(scene['id']+': camera id mismatch')
        for key in ['position_m','look_at_m']:
            v=cam.get(key,[])
            if len(v)!=3 or any(not isinstance(x,(int,float)) or not math.isfinite(x) for x in v): errors.append(scene['id']+': invalid camera '+key)
        if cam.get('position_m')==cam.get('look_at_m'): errors.append(scene['id']+': degenerate camera')
        if not isinstance(cam.get('focal_mm'),(int,float)) or cam['focal_mm']<=0: errors.append(scene['id']+': invalid focal length')
        for key in ['native','final','share','prompt']:
            value=scene.get(key)
            if not value:
                if c['release_kind']=='documented_case_study': errors.append(scene['id']+': missing '+key)
                continue
            try:
                p=inside(root,value)
                if not p.is_file(): errors.append(scene['id']+': missing file '+value)
                elif key in ['native','final']:
                    actual=image_size(p)
                    if actual!=scene.get(key+'_dimensions'): errors.append(scene['id']+': '+key+' dimensions mismatch')
            except WorkflowError as e: errors.append(str(e))
        dims=scene.get('native_dimensions',[0,0])
        if scene.get('native_4k') is True and (len(dims)!=2 or dims[0]<3840 or dims[1]<2160): errors.append(scene['id']+': false native 4K claim')
        if scene.get('expert_review')!='PASS': warnings.append(scene['id']+': independent archaeological review not confirmed')
        if scene.get('strict_pixel_mesh_fit')!='PASS': warnings.append(scene['id']+': strict image/mesh agreement not confirmed')
        if scene.get('known_issue'): warnings.append(scene['id']+': '+scene['known_issue'])
    for key in ['recipe','context_recipe']:
        if c['geometry'].get(key):
            try:
                if not inside(root,c['geometry'][key]).is_file(): errors.append('missing geometry recipe: '+key)
            except WorkflowError as e: errors.append(str(e))
    for x in c.get('external_assets',[]):
        if x.get('availability')=='NOT_BUNDLED_RIGHTS': warnings.append('external research asset excluded: '+x['id'])
    for f in c.get('failures',[]):
        for key in ['before','after']:
            if f.get(key) and not inside(root,f[key]).is_file(): errors.append(f['id']+': missing '+key+' comparison')
        for rel in f.get('evidence',[]):
            if not inside(root,rel).is_file(): errors.append(f['id']+': missing evidence '+rel)
    latest={}
    for review in c.get('reviews',[]):
        if review.get('scene_id') not in indexes.get('scenes',set()): errors.append('review refers to unknown scene')
        if review.get('status') not in ['PASS','FAIL','UNVERIFIED']: errors.append('invalid review status')
        scene=next((s for s in c['scenes'] if s['id']==review.get('scene_id')),None)
        target=review.get('target_sha256')
        if target and scene and scene.get('native'):
            try:
                if target!=review_target(c,scene,root):
                    warnings.append(scene['id']+': historical review belongs to an older image/evidence context')
                    continue
            except (WorkflowError,OSError,KeyError):continue
        latest[(review.get('scene_id'),review.get('criterion'))]=review
    for review in latest.values():
        if review['status']=='FAIL': errors.append('unresolved review failure: '+review['scene_id']+'/'+review['criterion'])
    imported_scenes={r.get('scene_id') for r in c.get('new_generation_records',[])}
    for scene in c['scenes']:
        if scene['id'] in imported_scenes:
            for criterion in ['geometry','chronology']:
                review=latest.get((scene['id'],criterion))
                if not review or not review.get('target_sha256'):
                    errors.append(scene['id']+': current image/evidence context needs a '+criterion+' review')
    if hashes:
        mp=root/c.get('manifest','assets.sha256.json')
        if not mp.is_file(): errors.append('missing asset manifest; run freeze only after reviewing deliberate changes')
        else:
            try: errors.extend(check_manifest(root,load(mp)))
            except WorkflowError as e: errors.append(str(e))
    return {'status':'FAIL' if errors else 'PASS','scope':'case structure, references, file integrity and declared dimensions','historical_accuracy':'UNVERIFIED','fresh_ai_generation':'NOT_RUN','errors':errors,'warnings':warnings,'counts':{k:len(c[k]) for k in ['sources','claims','components','scenes']}}

def mesh_invariants(mesh, expected):
    names=[m['id'] for m in mesh['objects']]
    patterns={'Apadana_main':r'^Apadana_col_\d+_\d+_shaft$','Apadana_three_porticoes':r'^Apadana_[NWE]_portico_col_\d+_\d+_shaft$','Hundred_main':r'^Hundred_col_\d+_\d+_shaft$','Hundred_north_portico':r'^Hundred_N_portico_col_\d+_\d+_shaft$','Gate':r'^Gate_col_\d+_\d+_shaft$','Tachara_main':r'^Tachara_col_\d+_\d+_shaft$','Hadish_main':r'^Hadish_col_\d+_\d+_shaft$','Tripylon':r'^Tripylon_col_\d+_\d+_shaft$'}
    actual={k:sum(bool(re.match(patterns[k],n)) for n in names) for k in expected if k in patterns}
    errors=[f'{k}: expected {v}, got {actual.get(k)}' for k,v in expected.items() if actual.get(k)!=v]
    if not names: errors.append('empty mesh')
    for m in mesh['objects']:
        if any(len(v)!=3 or any(not math.isfinite(x) for x in v) for v in m['vertices']): errors.append('nonfinite mesh vertex')
        if any(any(not isinstance(i,int) or i<0 or i>=len(m['vertices']) for i in f) for f in m['faces']): errors.append('invalid face index')
    return {'status':'FAIL' if errors else 'PASS','actual':actual,'errors':errors,'scope':'reference model, not generated-image column counts'}
