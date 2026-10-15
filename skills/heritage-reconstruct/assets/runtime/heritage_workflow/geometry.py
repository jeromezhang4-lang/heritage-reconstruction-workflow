"""Portable reference geometry. Metres; no external dependencies; not a survey."""
from pathlib import Path
import hashlib
import html
import math

def sub(a, b):
    return [x-y for x, y in zip(a, b)]

def dot(a, b):
    return sum(x*y for x, y in zip(a, b))

def cross(a, b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]

def norm(v):
    length = math.sqrt(dot(v, v))
    if length < 1e-12:
        raise ValueError('Degenerate vector/camera')
    return [x/length for x in v]

class Model:
    def __init__(self):
        self.meshes = []

    def mesh(self, id, vertices, faces, color=(185,165,127), tags=None):
        self.meshes.append({'id':id, 'vertices':[[float(x) for x in v] for v in vertices], 'faces':[list(f) for f in faces], 'color':list(color), 'tags':tags or ['all']})

    def box(self, id, center, size, color=(185,165,127), tags=None, rotation_deg=0):
        a = math.radians(rotation_deg)
        c, s = math.cos(a), math.sin(a)
        v = []
        for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
            x,y,z = i*size[0]/2, j*size[1]/2, k*size[2]/2
            v.append([c*x-s*y+center[0], s*x+c*y+center[1], z+center[2]])
        self.mesh(id,v,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],color,tags)

    def cylinder(self, id, center, radius, height, color=(185,165,127), tags=None, n=20, top_radius=None):
        x,y,z = center
        rr = radius if top_radius is None else top_radius
        v = [[x+r*math.cos(2*math.pi*i/n), y+r*math.sin(2*math.pi*i/n), z+h] for h,r in [(0,radius),(height,rr)] for i in range(n)]
        f = [[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)] + [list(range(n-1,-1,-1)),list(range(n,2*n))]
        self.mesh(id,v,f,color,tags)

    def wall(self, id, points, width, height, color=(185,165,127), tags=None):
        for p,q in zip(points,points[1:]):
            p,q = list(p),list(q)
            if len(p)==2: p.append(0)
            if len(q)==2: q.append(0)
            dx,dy=q[0]-p[0],q[1]-p[1]
            length=math.hypot(dx,dy)
            if length<1e-6: continue
            side=[-dy/length*width/2, dx/length*width/2]
            v=[[point[0]+sgn*side[0],point[1]+sgn*side[1],point[2]+dz] for dz in [0,height] for point,sgn in [(p,-1),(q,-1),(q,1),(p,1)]]
            self.mesh(id,v,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],color,tags)

    def ground(self, id, bounds, fn=lambda x,y:0, color=(164,149,118), tags=None, n=24):
        x0,y0,x1,y1=bounds
        v=[[x0+(x1-x0)*i/(n-1), y0+(y1-y0)*j/(n-1), 0] for j in range(n) for i in range(n)]
        for p in v: p[2]=fn(p[0],p[1])
        f=[]
        for j in range(n-1):
            for i in range(n-1):
                k=j*n+i
                f.extend([[k,k+1,k+n+1],[k,k+n+1,k+n]])
        self.mesh(id,v,f,color,tags)

    def as_dict(self):
        return {'units':'metres','coordinate_frame':'local approximate coordinates; not georeferenced','objects':[{'id':m['id'],'vertices':[[round(x,4) for x in v] for v in m['vertices']],'faces':m['faces'],'color':m['color']} for m in self.meshes]}

    def export_obj(self, path):
        path=Path(path)
        path.parent.mkdir(parents=True,exist_ok=True)
        lines=['# Evidence-constrained low-precision ARMS model; metres; not a certified survey']
        offset=1
        for m in self.meshes:
            lines.append('o '+m['id'])
            lines.extend('v '+' '.join(f'{x:.5f}' for x in p) for p in m['vertices'])
            lines.extend('f '+' '.join(str(int(i)+offset) for i in f) for f in m['faces'])
            offset+=len(m['vertices'])
        path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def svg(self, camera, path, width=960, height=540):
        """Projected object bounds for camera inspection, not an occlusion/raster render."""
        eye=camera['position_m']; f=norm(sub(camera['look_at_m'],eye))
        r=norm(cross(f,[0,0,1])); u=cross(r,f); scale=width*camera['focal_mm']/36
        parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#e7ece6"/>']
        edges=[(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
        for m in self.meshes:
            bounds=[(min(p[i] for p in m['vertices']),max(p[i] for p in m['vertices'])) for i in range(3)]
            vv=[[bounds[0][i],bounds[1][j],bounds[2][k]] for i,j,k in [(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]]
            points=[]
            for p in vv:
                d=sub(p,eye);z=dot(d,f)
                points.append(None if z<=.2 else (width/2+scale*dot(d,r)/z,height/2-scale*dot(d,u)/z))
            commands=[]
            for i,j in edges:
                a,b=points[i],points[j]
                if a is not None and b is not None and all(abs(q)<100000 for q in (*a,*b)):
                    commands.append(f'M{a[0]:.2f},{a[1]:.2f}L{b[0]:.2f},{b[1]:.2f}')
            if commands:
                parts.append('<path d="'+' '.join(commands)+'" fill="none" stroke="#4b6256" stroke-width=".45" opacity=".65"/>')
        parts.append('<rect width="100%" height="30" fill="#e7ece6"/><text x="12" y="21" font-size="14">'+html.escape(camera['id']+' · object-bounds camera preview; not a depth render')+'</text></svg>')
        Path(path).write_text(''.join(parts),encoding='utf-8')
