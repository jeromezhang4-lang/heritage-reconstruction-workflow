"""Optional original NumPy/Pillow depth renderer, retained from the case process (MIT)."""
"""Actual low-resolution archaeological reference mesh renderer, not a final AI image."""
from pathlib import Path
import hashlib, json, math, time
import numpy as np
from PIL import Image, ImageFilter

class Model:
    def __init__(self):self.meshes=[]
    def mesh(self,id,vertices,faces,color=(185,165,127),tags=None):
        self.meshes.append({'id':id,'vertices':np.asarray(vertices,float),'faces':[np.asarray(f,int) for f in faces],'color':color,'tags':tags or ['all']})
    def box(self,id,center,size,color=(185,165,127),tags=None,rotation_deg=0):
        c=np.asarray(center,float);s=np.asarray(size,float)/2
        v=np.asarray([[i*s[0],j*s[1],k*s[2]] for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]])
        a=math.radians(rotation_deg);r=np.asarray([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
        v=v@r.T+c
        self.mesh(id,v,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],color,tags)
    def cylinder(self,id,center,radius,height,color=(185,165,127),tags=None,n=20,top_radius=None):
        x,y,z=center;rr=radius if top_radius is None else top_radius
        v=[[x+r*math.cos(2*math.pi*i/n),y+r*math.sin(2*math.pi*i/n),z+h] for h,r in [(0,radius),(height,rr)] for i in range(n)]
        f=[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]+[list(range(n-1,-1,-1)),list(range(n,2*n))]
        self.mesh(id,v,f,color,tags)
    def wall(self,id,points,width,height,color=(185,165,127),tags=None):
        for p,q in zip(points,points[1:]):
            p=np.asarray(p,float);q=np.asarray(q,float)
            if len(p)==2:p=np.r_[p,0]
            if len(q)==2:q=np.r_[q,0]
            d=q[:2]-p[:2];length=np.linalg.norm(d)
            if length<1e-6:continue
            u=d/length;side=np.asarray([-u[1],u[0]])*width/2
            v=[]
            for dz in [0,height]:
                for point,sgn in [(p,-1),(q,-1),(q,1),(p,1)]:v.append([*(point[:2]+sgn*side),point[2]+dz])
            self.mesh(id,v,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],color,tags)
    def ground(self,id,bounds,fn=lambda x,y:0,color=(164,149,118),tags=None,n=24):
        x0,y0,x1,y1=bounds;v=[[x,y,fn(x,y)] for y in np.linspace(y0,y1,n) for x in np.linspace(x0,x1,n)]
        f=[]
        for j in range(n-1):
            for i in range(n-1):k=j*n+i;f.extend([[k,k+1,k+n+1],[k,k+n+1,k+n]])
        self.mesh(id,v,f,color,tags)
    def export_obj(self,path):
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);lines=['# Evidence-constrained low-precision ARMS model; metres; not a certified survey'];offset=1
        for m in self.meshes:
            lines.append('o '+m['id'])
            lines.extend('v '+' '.join(f'{x:.5f}' for x in p) for p in m['vertices'])
            lines.extend('f '+' '.join(str(int(i)+offset) for i in f) for f in m['faces']);offset+=len(m['vertices'])
        path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        return hashlib.sha256(path.read_bytes()).hexdigest()
    @staticmethod
    def clip(poly,near=.12):
        out=[]
        for a,b in zip(poly,poly[1:]+poly[:1]):
            ia=a[2]>=near;ib=b[2]>=near
            if ia:out.append(a)
            if ia!=ib:out.append(a+(b-a)*((near-a[2])/(b[2]-a[2])))
        return out
    def render(self,camera,path,width=1280,height=720,deadline=120):
        start=time.monotonic();path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        rgb=np.full((height,width,3),(192,209,215),dtype=np.uint8);depth=np.full((height,width),np.inf)
        p=np.asarray(camera['position_m'],float);target=np.asarray(camera['look_at_m'],float);forward=target-p;forward/=np.linalg.norm(forward)
        right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward);basis=np.asarray([right,up,forward]);fx=width*camera['focal_mm']/36
        tags=camera.get('tags',['all']);triangles=0;objects=0
        for m in self.meshes:
            if 'all' not in tags and 'all' not in m['tags'] and not set(tags).intersection(m['tags']):continue
            objects+=1;cv=(m['vertices']-p)@basis.T
            for face in m['faces']:
                wp=m['vertices'][face];normal=np.cross(wp[1]-wp[0],wp[2]-wp[0]);length=np.linalg.norm(normal)
                if length<1e-9:continue
                light=.68+.32*abs(float(normal/length@np.asarray([.35,-.4,.847])));color=np.clip(np.asarray(m['color'])*light,0,255).astype(np.uint8)
                cp=self.clip([x.copy() for x in cv[face]])
                for j in range(1,len(cp)-1):
                    v=np.asarray([cp[0],cp[j],cp[j+1]]);iz=1/v[:,2];s=np.column_stack((width/2+fx*v[:,0]*iz,height/2-fx*v[:,1]*iz))
                    if not np.isfinite(s).all():continue
                    x0=max(0,int(np.floor(s[:,0].min())));x1=min(width-1,int(np.ceil(s[:,0].max())))
                    y0=max(0,int(np.floor(s[:,1].min())));y1=min(height-1,int(np.ceil(s[:,1].max())))
                    if x0>x1 or y0>y1:continue
                    a,b,c=s;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
                    if abs(den)<1e-10:continue
                    X,Y=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
                    u=((b[1]-c[1])*(X-c[0])+(c[0]-b[0])*(Y-c[1]))/den;v=((c[1]-a[1])*(X-c[0])+(a[0]-c[0])*(Y-c[1]))/den;w=1-u-v
                    z=1/np.maximum(u*iz[0]+v*iz[1]+w*iz[2],1e-10);region=depth[y0:y1+1,x0:x1+1];mask=(u>=-1e-8)&(v>=-1e-8)&(w>=-1e-8)&(z<region)
                    region[mask]=z[mask];rgb[y0:y1+1,x0:x1+1][mask]=color;triangles+=1
            if time.monotonic()-start>deadline:raise TimeoutError('Reference renderer reached bounded deadline')
        Image.fromarray(rgb).save(path)
        finite=np.isfinite(depth);dep=np.zeros(depth.shape,dtype=np.uint8)
        if finite.any():
            a,b=np.percentile(depth[finite],[1,99]);dep[finite]=np.clip(255*(b-depth[finite])/max(b-a,1e-6),0,255).astype(np.uint8)
        depth_path=path.with_name(path.stem.replace('_Structure','')+'_Depth.png');Image.fromarray(dep).save(depth_path)
        edge_path=path.with_name(path.stem.replace('_Structure','')+'_Edges.png');Image.fromarray(rgb).convert('L').filter(ImageFilter.FIND_EDGES).save(edge_path)
        return {'status':'ACTUAL_MESH_RENDER','dimensions':[width,height],'objects':objects,'triangles':triangles,'elapsed_seconds':round(time.monotonic()-start,3),'visible_pixels':int(finite.sum()),'not_final_ai_image':True,'structure_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'depth':str(depth_path),'edges':str(edge_path)}
