from pathlib import Path
import hashlib
import json
import struct

class WorkflowError(ValueError):
    pass

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def load(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError,ValueError) as e:
        raise WorkflowError(f'Cannot read JSON {Path(path).name}: {e}') from e

def dump(path, data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def inside(root, relative):
    root=Path(root).resolve()
    relative=Path(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise WorkflowError(f'Expected a relative path inside the case: {relative}')
    candidate=(root/relative).resolve()
    if not candidate.is_relative_to(root):
        raise WorkflowError('Path escapes the case directory')
    return candidate

def image_size(path):
    with Path(path).open('rb') as f:
        head=f.read(24)
        if head[:8]==b'\x89PNG\r\n\x1a\n' and len(head)>=24:
            return list(struct.unpack('>II',head[16:24]))
        f.seek(0)
        if f.read(2)!=b'\xff\xd8':
            raise WorkflowError(f'Only PNG/JPEG image files are supported: {Path(path).name}')
        while True:
            marker=f.read(1)
            if not marker: break
            if marker!=b'\xff': continue
            while marker==b'\xff': marker=f.read(1)
            if not marker: break
            tag=marker[0]
            if tag in [0xD8,0xD9] or 0xD0<=tag<=0xD7: continue
            raw=f.read(2)
            if len(raw)!=2: break
            size=struct.unpack('>H',raw)[0]
            if size<2: break
            if tag in [0xC0,0xC1,0xC2,0xC3,0xC5,0xC6,0xC7,0xC9,0xCA,0xCB,0xCD,0xCE,0xCF]:
                raw=f.read(5)
                if len(raw)!=5: break
                _,h,w=struct.unpack('>BHH',raw)
                return [w,h]
            f.seek(size-2,1)
    raise WorkflowError(f'Cannot read image dimensions: {Path(path).name}')

def manifest(root, exclude=()):
    root=Path(root)
    return {p.relative_to(root).as_posix():sha(p) for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and '.git' not in p.parts and p.relative_to(root).as_posix() not in exclude}

def check_manifest(root, entries):
    errors=[]
    for rel, expected in entries.items():
        path=inside(root,rel)
        if not path.is_file(): errors.append('missing asset: '+rel)
        elif sha(path)!=expected: errors.append('asset hash mismatch: '+rel)
    return errors
