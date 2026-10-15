from pathlib import Path
import importlib.util
import json
import re
import zipfile
from .geometry import Model
from .io import WorkflowError, dump, load, sha, manifest, check_manifest, inside
from .validation import verify_case, mesh_invariants

def output_dir(path, case_id):
    p=Path(path).resolve()
    marker=p/'.heritage-build.json'
    if p.exists() and any(p.iterdir()):
        if not marker.is_file() or load(marker).get('case_id')!=case_id:
            raise WorkflowError('Output directory is not empty or owned by this case; choose a new directory')
    p.mkdir(parents=True,exist_ok=True)
    dump(marker,{'case_id':case_id,'format':'heritage-build-1'})
    return p

def module(path):
    spec=importlib.util.spec_from_file_location('heritage_case_recipe',path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def primitive_model(data):
    m=Model()
    for item in data.get('boxes',[]):
        m.box(item['id'],item['center'],item['size'],item.get('color',[194,180,149]))
    for item in data.get('column_grids',[]):
        nx,ny=item['count']; x,y,z=item['origin']; dx,dy=item['spacing']
        for i in range(nx):
            for j in range(ny):
                m.cylinder(f"{item['id']}_{i}_{j}",[x+i*dx,y+j*dy,z],item['radius'],item['height'],n=12)
    return m

def prepare(root, out):
    root=Path(root).resolve(); c=load(root/'case.json')
    report=verify_case(root,hashes=True)
    if report['status']!='PASS':
        raise WorkflowError('Case validation failed: '+'; '.join(report['errors'][:8]))
    out=Path(out).resolve()
    if out==root or out.is_relative_to(root):
        raise WorkflowError('Build output must be outside the case input directory')
    out=output_dir(out,c['id'])
    geo=c['geometry']
    if geo.get('recipe'):
        model,components,cameras=module(inside(root,geo['recipe'])).create()
    else:
        model=primitive_model(load(inside(root,geo['data'])))
        components=c['components'];cameras=[s['camera'] for s in c['scenes']]
    core=model.as_dict()
    errors=[]
    if geo.get('expected_objects',{}).get('core') not in [None,len(core['objects'])]: errors.append('core object count mismatch')
    invariant=mesh_invariants(core,geo.get('column_invariants',{}))
    errors.extend(invariant['errors'])
    # A recorded-case comparison checks numerical geometry, not image correspondence.
    original=root/'recorded/02_Model/mesh.json'
    max_delta=0.0
    if original.is_file():
        old=load(original)['objects']
        if len(old)!=len(core['objects']): errors.append('recorded mesh object count differs')
        else:
            for a,b in zip(old,core['objects']):
                if a['id']!=b['id'] or a['faces']!=b['faces'] or len(a['vertices'])!=len(b['vertices']):
                    errors.append('recorded mesh topology differs: '+a['id']);continue
                max_delta=max(max_delta,max((abs(x-y) for p,q in zip(a['vertices'],b['vertices']) for x,y in zip(p,q)),default=0))
            if max_delta>.000101: errors.append('recorded geometry differs by more than 0.000101 metre')
    if errors: raise WorkflowError('; '.join(errors[:8]))
    core_sha=model.export_obj(out/'model/core.obj')
    dump(out/'model/core.json',core)
    models={'core':core};objects={'core':len(core['objects'])};obj_hashes={'core':core_sha}
    if geo.get('context_recipe'):
        context,regions,cam=module(inside(root,geo['context_recipe'])).create_context(core)
        ctx=context.as_dict();expected=geo.get('expected_objects',{}).get('context')
        if expected is not None and len(ctx['objects'])!=expected: raise WorkflowError('context object count mismatch')
        context_delta=0.0
        context_baseline=root/'recorded/02_Model/context_mesh.json'
        if context_baseline.is_file():
            old=load(context_baseline)['objects']
            if len(old)!=len(ctx['objects']):raise WorkflowError('recorded context object count differs')
            for a,b in zip(old,ctx['objects']):
                if a['id']!=b['id'] or a['faces']!=b['faces'] or len(a['vertices'])!=len(b['vertices']):raise WorkflowError('recorded context topology differs')
                context_delta=max(context_delta,max((abs(x-y) for p,q in zip(a['vertices'],b['vertices']) for x,y in zip(p,q)),default=0))
            if context_delta>.000201:raise WorkflowError('recorded context geometry differs beyond saved precision')
        models['context']=ctx;objects['context']=len(ctx['objects'])
        obj_hashes['context']=context.export_obj(out/'model/context.obj')
        dump(out/'model/context.json',ctx);dump(out/'model/regions.json',regions)
        cameras.append(cam)
    dump(out/'model/cameras.json',cameras)
    references=out/'references';references.mkdir(exist_ok=True)
    for camera in cameras:
        if camera['id'] not in {s['id'] for s in c['scenes']}: raise WorkflowError('Recipe camera has no scene')
        expected=next(s['camera'] for s in c['scenes'] if s['id']==camera['id'])
        if any(camera[k]!=expected[k] for k in ['position_m','look_at_m','focal_mm']): raise WorkflowError('Recipe/case camera mismatch')
        source=Model();source.meshes=models['context' if camera.get('kind')=='regional' else 'core']['objects']
        source.svg(camera,references/(camera['id']+'.svg'))
    report.update({'model_objects':objects,'column_invariants':invariant,'recorded_core_max_coordinate_delta_m':max_delta,'recorded_context_max_coordinate_delta_m':context_delta if geo.get('context_recipe') else None,'obj_sha256':obj_hashes,'reference_format':'SVG projected object bounds; original raster references are separately preserved','case_json_sha256':sha(root/'case.json')})
    dump(out/'technical-report.json',report)
    return c,out,models,report

def reproduce(root,out,make_zip=True):
    from .gallery import build_gallery
    c,out,models,report=prepare(root,out)
    if any(not s.get('share') for s in c['scenes']):
        raise WorkflowError('This draft has no complete result set. Use prepare, then record-generation and human review before building a gallery.')
    build_gallery(root,c,out,models)
    report['gallery']='gallery.html'
    report['status']='PASS'
    report['replay_scope']='regenerated reference geometry/cameras/SVG previews + recorded image replay + offline gallery + integrity checks'
    report['ai_images_regenerated']=False
    report['historical_accuracy']='UNVERIFIED'
    report['known_visual_issues']=[s['id'] for s in c['scenes'] if s.get('known_issue')]
    dump(out/'technical-report.json',report)
    dump(out/'BUILD_MANIFEST.json',manifest(out,exclude=['BUILD_MANIFEST.json','case-release.zip','ZIP_VERIFICATION.json']))
    if make_zip:
        pack_build(out,out/'case-release.zip')
    return report

def pack_build(root,archive):
    root=Path(root).resolve();archive=Path(archive).resolve()
    entries=load(root/'BUILD_MANIFEST.json')
    errors=check_manifest(root,entries)
    if errors: raise WorkflowError('; '.join(errors[:8]))
    names=sorted([*entries,'BUILD_MANIFEST.json'])
    if archive==root/'BUILD_MANIFEST.json' or archive in [root/name for name in names]: raise WorkflowError('Archive would overwrite an input')
    archive.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=4) as z:
        for name in names: z.write(root/name,name)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None: raise WorkflowError('ZIP CRC failure')
        hashes={n:__import__('hashlib').sha256(z.read(n)).hexdigest() for n in z.namelist()}
    for name,expected in entries.items():
        if hashes.get(name)!=expected: raise WorkflowError('ZIP member differs from build: '+name)
    result={'status':'PASS','archive_sha256':sha(archive),'members':len(hashes),'member_sha256':hashes,'scope':'CRC, member hashes and same-build-file readback'}
    dump(archive.with_name('ZIP_VERIFICATION.json'),result)
    return result
