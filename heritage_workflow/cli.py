"""CLI: no credentials, network requests or AI generation in the offline route."""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import json
import shutil
import struct
import sys
import zlib
from . import __version__
from .io import WorkflowError, load, dump, manifest, inside, sha, image_size
from .validation import verify_case, review_target
from .pipeline import prepare, reproduce

def freeze(root):
    root=Path(root).resolve()
    report=verify_case(root,hashes=False)
    if report['status']!='PASS': raise WorkflowError('; '.join(report['errors'][:8]))
    dump(root/'assets.sha256.json',manifest(root,exclude=['assets.sha256.json']))
    return {'status':'PASS','scope':'deliberate case snapshot only; not historical certification','files':len(load(root/'assets.sha256.json'))}

def init_case(path,name,demo=False):
    root=Path(path).resolve()
    if root.exists() and any(root.iterdir()): raise WorkflowError('Case destination must be empty')
    root.mkdir(parents=True,exist_ok=True)
    if not name or not __import__('re').fullmatch('[a-z0-9][a-z0-9-]{0,63}',name): raise WorkflowError('Use a lowercase, hyphenated case id')
    camera={'id':'SC01','position_m':[-38,48,32],'look_at_m':[0,0,4],'focal_mm':30,'kind':'overall'}
    c={'schema_version':'1.0','id':name,'title':name+(' · SYNTHETIC DEMO' if demo else ' · RESEARCH DRAFT'),'title_en':name,'snapshot_bce':None,'release_kind':'documented_case_study' if demo else 'reconstruction_draft','sources':[{'id':'S01','title':'Synthetic fixture, not a historical source' if demo else 'Replace with an inspected primary/academic source','url':'https://example.org/heritage-synthetic-demo' if demo else 'https://example.org/replace-me','access':'Synthetic data supplied to exercise the tools; no archaeological claim' if demo else 'NOT_YET_READ','placeholder':not demo}],'claims':[{'id':'T01','text':'Synthetic rectangular hall' if demo else 'Replace with a sourced architectural claim','source_ids':['S01'],'certainty':['D'] if demo else ['UNKNOWN'],'limitation':'Synthetic geometry for software exercise; not evidence of any ancient building' if demo else 'Plan, dimensions and chronology not yet established'}],'components':[{'id':'hall','dimensions_m':[20,24,8],'claim_ids':['T01'],'reconstruction_tiers':{'all':'D'}}],'scenes':[{'id':'SC01','title_zh':'Synthetic demo' if demo else 'Scene to be researched','title_en':'Synthetic software exercise' if demo else 'Research draft','kind':'overall','camera':camera,'claim_ids':['T01'],'component_ids':['hall'],'approval':'synthetic_fixture' if demo else 'draft','zh':['合成软件样例，不对应任何古代遗址。'],'en':['Synthetic software fixture, not an archaeological reconstruction.'],'expert_review':'NOT_PERFORMED','strict_pixel_mesh_fit':'UNVERIFIED'}],'geometry':{'data':'geometry.json','column_invariants':{}},'limitations':['SYNTHETIC: no historical accuracy is claimed.' if demo else 'DRAFT: replace all placeholders and document unknowns before any historical release.'],'external_assets':[],'failures':[],'reviews':[],'manifest':'assets.sha256.json'}
    dump(root/'geometry.json',{'boxes':[{'id':'hall_floor','center':[0,0,0],'size':[24,28,1]},{'id':'hall_roof','center':[0,0,8],'size':[24,28,1]}],'column_grids':[{'id':'demo_column','origin':[-7,-9,0],'count':[3,4],'spacing':[7,6],'radius':.6,'height':8}]})
    if demo:
        def chunk(kind,body):return struct.pack('>I',len(body))+kind+body+struct.pack('>I',zlib.crc32(kind+body)&0xffffffff)
        w,h=16,9
        raw=b''.join(b'\0'+bytes([175,151,104])*w for _ in range(h))
        png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
        (root/'synthetic.png').write_bytes(png);(root/'synthetic.prompt.txt').write_text('Synthetic fixture. Not an AI call or historical image.\n')
        c['scenes'][0].update(native='synthetic.png',final='synthetic.png',share='synthetic.png',prompt='synthetic.prompt.txt',native_dimensions=[w,h],final_dimensions=[w,h],native_4k=False,actual_tool='synthetic_fixture_not_ai')
    dump(root/'case.json',c)
    if demo: freeze(root)
    return {'status':'PASS','case':name,'mode':'SYNTHETIC_DEMO' if demo else 'DRAFT_REQUIRES_RESEARCH','next':'reproduce' if demo else 'replace source/claim/geometry placeholders, verify --no-hashes, then freeze'}

def record_generation(args):
    root=Path(args.case).resolve();c=load(root/'case.json')
    scene=next((s for s in c['scenes'] if s['id']==args.scene),None)
    if scene is None: raise WorkflowError('Unknown scene id')
    image=Path(args.image).resolve();prompt=Path(args.prompt).resolve()
    dims=image_size(image)
    if not prompt.is_file(): raise WorkflowError('Prompt file is missing')
    reference_paths=[Path(p).resolve() for p in args.reference or []]
    if any(not p.is_file() for p in reference_paths): raise WorkflowError('Reference does not exist')
    records=c.setdefault('new_generation_records',[])
    attempt=1+sum(r['scene_id']==args.scene for r in records)
    folder=inside(root,f'generated/{args.scene}/attempt-{attempt:03d}')
    folder.mkdir(parents=True,exist_ok=False)
    dst=folder/('native'+image.suffix.lower());shutil.copyfile(image,dst)
    pp=folder/'prompt.txt';shutil.copyfile(prompt,pp)
    refs=[]
    for i,p in enumerate(reference_paths):
        rp=folder/f'reference-{i+1}{p.suffix.lower()}';shutil.copyfile(p,rp)
        refs.append({'path':rp.relative_to(root).as_posix(),'sha256':sha(rp)})
    rec={'scene_id':args.scene,'attempt':attempt,'tool':args.tool,'provider_model':args.model or 'UNVERIFIED_NOT_EXPOSED','seed':args.seed or 'UNVERIFIED_NOT_EXPOSED','native':dst.relative_to(root).as_posix(),'native_sha256':sha(dst),'native_dimensions':dims,'prompt':pp.relative_to(root).as_posix(),'prompt_sha256':sha(pp),'references':refs,'recorded_at_utc':datetime.now(timezone.utc).isoformat(),'verification_scope':'local input/output files and caller-supplied tool identity; not provider attestation'}
    records.append(rec)
    # No silent upscaling: initially the native image is also the share/final asset.
    scene.update(native=rec['native'],final=rec['native'],share=rec['native'],prompt=rec['prompt'],native_dimensions=dims,final_dimensions=dims,native_4k=dims[0]>=3840 and dims[1]>=2160,approval='UNREVIEWED',expert_review='NOT_PERFORMED',strict_pixel_mesh_fit='UNVERIFIED')
    dump(root/'case.json',c)
    return {'status':'RECORDED_NOT_REVIEWED','record':rec,'next':'review actual image against source/geometry/chronology; record-review; freeze only after deliberate review'}

def record_review(args):
    root=Path(args.case);c=load(root/'case.json')
    scene=next((s for s in c['scenes'] if s['id']==args.scene),None)
    if scene is None:raise WorkflowError('Unknown scene id')
    if not scene.get('native'):raise WorkflowError('No actual image to review')
    review={'scene_id':args.scene,'criterion':args.criterion,'status':args.status,'note':args.note,'reviewer':args.reviewer,'target_sha256':review_target(c,scene,root),'native_sha256':sha(inside(root,scene['native'])),'recorded_at_utc':datetime.now(timezone.utc).isoformat()}
    c.setdefault('reviews',[]).append(review);dump(root/'case.json',c)
    return {'status':'RECORDED','review':review,'next':'geometry and chronology reviews must refer to the current image/evidence context; unresolved FAIL blocks release; freeze after deliberate review'}

def main(argv=None):
    p=argparse.ArgumentParser(description='Evidence-aware historical reconstruction workflow; offline replay is not fresh AI generation.')
    p.add_argument('--version',action='version',version=__version__)
    sub=p.add_subparsers(dest='command',required=True)
    for cmd in ['verify','freeze','audit']:
        q=sub.add_parser(cmd);q.add_argument('--case',required=True)
        if cmd=='verify':q.add_argument('--no-hashes',action='store_true',help='structure check for deliberate edits; not release verification')
        if cmd=='audit':q.add_argument('--report',required=True)
    for cmd in ['prepare','reproduce']:
        q=sub.add_parser(cmd);q.add_argument('--case',required=True);q.add_argument('--out',required=True)
        if cmd=='reproduce':q.add_argument('--no-zip',action='store_true')
    q=sub.add_parser('init');q.add_argument('--out',required=True);q.add_argument('--id',required=True);q.add_argument('--demo',action='store_true',help='synthetic runnable fixture, not an ancient site')
    q=sub.add_parser('record-generation');q.add_argument('--case',required=True);q.add_argument('--scene',required=True);q.add_argument('--image',required=True);q.add_argument('--prompt',required=True);q.add_argument('--tool',required=True);q.add_argument('--model');q.add_argument('--seed');q.add_argument('--reference',action='append')
    q=sub.add_parser('record-review');q.add_argument('--case',required=True);q.add_argument('--scene',required=True);q.add_argument('--criterion',required=True,choices=['chronology','geometry','materials','scale','anatomy','scope','image_mesh_fit']);q.add_argument('--status',required=True,choices=['PASS','FAIL','UNVERIFIED']);q.add_argument('--note',required=True);q.add_argument('--reviewer',required=True)
    q=sub.add_parser('render-raster');q.add_argument('--build',required=True);q.add_argument('--scene',required=True);q.add_argument('--out',required=True);q.add_argument('--width',type=int,default=960);q.add_argument('--height',type=int,default=540);q.add_argument('--deadline',type=int,default=120)
    args=p.parse_args(argv)
    try:
        if args.command=='verify':result=verify_case(args.case,not args.no_hashes)
        elif args.command=='freeze':result=freeze(args.case)
        elif args.command=='audit':
            result=verify_case(args.case)
            result['manual_review_required']=['source interpretation and chronology','generated image geometry and guardian anatomy','modern intrusions, human scale and density','rights of any newly introduced external input']
            result['overall_historical_certification']='NOT_PROVIDED'
            dump(args.report,result)
        elif args.command=='prepare':result=prepare(args.case,args.out)[3]
        elif args.command=='reproduce':result=reproduce(args.case,args.out,not args.no_zip)
        elif args.command=='init':result=init_case(args.out,args.id,args.demo)
        elif args.command=='record-generation':result=record_generation(args)
        elif args.command=='record-review':result=record_review(args)
        else:
            try:from .raster import Model as RasterModel
            except ImportError as e:raise WorkflowError('Optional raster dependencies missing; install requirements-render.txt in your venv') from e
            build=Path(args.build);cams=load(build/'model/cameras.json')
            cam=next((c for c in cams if c['id']==args.scene),None)
            if not cam:raise WorkflowError('Unknown rendered scene')
            mesh=load(build/'model'/('context.json' if cam.get('kind')=='regional' else 'core.json'))
            rm=RasterModel()
            for m in mesh['objects']:rm.mesh(m['id'],m['vertices'],m['faces'],m['color'])
            dst=Path(args.out);dst.mkdir(parents=True,exist_ok=True)
            if args.width<64 or args.height<64 or args.width>3840 or args.height>2160 or not 1<=args.deadline<=600:raise WorkflowError('Invalid bounded raster dimensions/deadline')
            result=rm.render(cam,dst/(args.scene+'_Structure.png'),width=args.width,height=args.height,deadline=args.deadline)
            result['depth']=Path(result['depth']).name;result['edges']=Path(result['edges']).name
            dump(dst/'RASTER_RECEIPT.json',result)
        print(json.dumps(result,ensure_ascii=True,indent=2))
        return 1 if result.get('status')=='FAIL' else 0
    except (WorkflowError,OSError,ValueError,KeyError,TypeError) as e:
        print(json.dumps({'status':'FAIL','error':str(e)},ensure_ascii=True),file=sys.stderr)
        return 2

if __name__=='__main__':
    sys.exit(main())
